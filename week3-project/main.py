# ===========================================
# main.py — Docs Copilot FastAPI 服务
# ===========================================
# AI 文档问答助手
# 技术栈: FastAPI + ChromaDB + SSE
#
# 用法:
#   1. 先索引文档: python week3-project/indexer.py
#   2. 启动服务: uvicorn week3-project.main:app --reload
#   3. 访问: http://localhost:8000
# ===========================================

import sys
import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from models import (
    IndexRequest, IndexResponse,
    AskRequest, AskResponse, SourceItem,
)
from rag import get_pipeline


# ===========================================
# 应用初始化
# ===========================================

app = FastAPI(
    title="Docs Copilot",
    description="AI 文档问答助手 — 基于 RAG 的知识检索",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """启动时初始化 RAG Pipeline"""
    pipeline = get_pipeline()
    count = pipeline.collection.count()
    print(f"\n[Docs Copilot] 启动完成")
    print(f"  向量库: {count} 条文档")
    print(f"  访问: http://localhost:8000\n")


# ===========================================
# 页面路由
# ===========================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """返回聊天页面"""
    index_html = Path(__file__).parent / "templates" / "index.html"
    if index_html.exists():
        return HTMLResponse(content=index_html.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse(content="<h1>模板文件不存在</h1>", status_code=500)


# ===========================================
# API 路由
# ===========================================

@app.get("/api/health")
def health():
    """健康检查"""
    pipeline = get_pipeline()
    return {
        "status": "ok",
        "docs_count": pipeline.collection.count(),
    }


@app.post("/api/index", response_model=IndexResponse)
def index_document(req: IndexRequest):
    """
    索引文档

    把文本分块后存入向量库
    """
    pipeline = get_pipeline()
    chunks = pipeline.index_text(req.text, source=req.source, chunk_size=req.chunk_size)

    if chunks == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "文档内容太短或为空"},
        )

    return IndexResponse(
        message=f"文档 '{req.source}' 索引成功",
        chunks_count=chunks,
        source=req.source,
    )


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """
    RAG 问答（非流式）

    检索相关文档 → AI 生成回答 → 返回结果
    """
    pipeline = get_pipeline()
    result = pipeline.ask(req.question, n_results=req.top_k)

    sources = [SourceItem(**s) for s in result["sources"]]

    return AskResponse(
        answer=result["answer"],
        sources=sources,
        question=result["question"],
    )


@app.post("/api/ask/stream")
async def ask_stream(req: AskRequest):
    """
    RAG 问答（SSE 流式输出）

    事件类型:
    - token: 每个文字片段
    - sources: 引用来源
    - done: 结束信号
    - error: 错误
    """
    pipeline = get_pipeline()

    # 先检索
    search_result = pipeline.search(req.question, n_results=req.top_k)

    if not search_result["context"]:
        async def empty_gen():
            yield {"event": "token", "data": json.dumps({"text": "知识库为空，请先添加文档。"})}
            yield {"event": "done", "data": json.dumps({"status": "complete"})}
        return EventSourceResponse(empty_gen())

    # 构造 prompt
    rag_prompt = f"""你是一个知识助手。根据以下参考文档回答用户的问题。
规则：
1. 只基于文档内容回答，不要编造
2. 如果文档中没有相关信息，明确说"根据现有文档无法回答这个问题"
3. 回答要简洁清晰

参考文档：
{search_result["context"]}

用户问题：{req.question}"""

    # 流式生成
    async def event_generator():
        try:
            stream = pipeline.ai_client.messages.create(
                model=pipeline.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": rag_prompt}],
                stream=True,
            )

            for event in stream:
                if event.type == "content_block_delta":
                    text = event.delta.text
                    if text:
                        yield {
                            "event": "token",
                            "data": json.dumps({"text": text}, ensure_ascii=False),
                        }
                        await asyncio.sleep(0.01)

            # 发送来源
            yield {
                "event": "sources",
                "data": json.dumps(search_result["sources"], ensure_ascii=False),
            }

            # 结束
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"}),
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


# ===========================================
# 启动
# ===========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
