# ===========================================
# Day 4: FastAPI 后端 — Python 版的 Express.js
# ===========================================
# FastAPI = Python 最流行的现代 Web 框架
# 如果你会 Express.js，FastAPI 10 分钟就能上手
#
# 核心卖点（对比 Express）：
# 1. 自带 API 文档 — 启动后访问 /docs 就有 Swagger UI
# 2. 内置 Pydantic — 请求/响应自动校验（不需要 Zod）
# 3. 原生 async — 和 Express 一样支持异步
# 4. 类型提示 — 自动生成 TypeScript 式的类型校验
#
# Express 老手迁移指南：
# app = express()        → app = FastAPI()
# app.get("/path", fn)   → @app.get("/path")
# req.params.id          → path 参数
# req.query.page         → Query 参数
# req.body               → Pydantic Model
# res.json({...})        → 直接 return dict
# app.listen(3000)       → uvicorn.run(app, port=8000)
# ===========================================

# 安装（如果还没装）：
# pip install fastapi uvicorn sse-starlette chromadb python-multipart

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask


# ===========================================
# 1. FastAPI 是什么？
# ===========================================
# FastAPI 就是 Python 版的 Express.js，但自带了很多 Express 需要插件才有的功能：
#
# | 功能 | Express | FastAPI |
# |------|---------|---------|
# | 路由 | app.get() | @app.get() |
# | 请求校验 | Zod / Joi | Pydantic（内置） |
# | API 文档 | Swagger 手动配 | 自动生成（/docs） |
# | 类型 | TypeScript | 类型提示（内置） |
# | 异步 | async/await | async/await |
#
# JS 类比：
# const express = require('express')
# const app = express()
#
# Python 等价：
# from fastapi import FastAPI
# app = FastAPI()

print("=== 1. FastAPI 是什么 ===\n")

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

# 创建应用 — 相当于 const app = express()
app = FastAPI(
    title="AI RAG API",               # 文档标题
    description="Week 3 Day 4 学习项目",  # 文档描述
    version="1.0.0",
)

# 最简单的路由 — 相当于 app.get("/", (req, res) => res.json({ message: "Hello" }))
@app.get("/")
def root():
    """
    根路由 — API 健康检查

    Express 等价代码：
    app.get("/", (req, res) => {
        res.json({ message: "Hello from FastAPI!" })
    })
    """
    return {"message": "Hello from FastAPI!", "docs": "访问 /docs 查看 API 文档"}

print("FastAPI 应用已创建")
print("启动后访问:")
print("  http://localhost:8000      → API 根路径")
print("  http://localhost:8000/docs → Swagger 文档（自动生成！）")
print("  http://localhost:8000/redoc → ReDoc 文档（另一种风格）\n")


# ===========================================
# 2. 第一个路由 — GET 请求
# ===========================================
# Express 写法:
#   app.get("/hello/:name", (req, res) => {
#       const { name } = req.params
#       const { greeting } = req.query
#       res.json({ message: `${greeting || 'Hello'}, ${name}!` })
#   })
#
# FastAPI 写法:
#   @app.get("/hello/{name}")
#   def hello(name: str, greeting: str = "Hello"):
#       return {"message": f"{greeting}, {name}!"}
#
# 关键区别：
# - Express 用 :name（冒号），FastAPI 用 {name}（花括号）
# - Express 手动从 req.params / req.query 取值
# - FastAPI 直接写在函数参数里，自动识别 path 参数 vs query 参数
# - FastAPI 有默认值 = query 参数；没有默认值 = 必填参数

# --- 2a. 简单 GET ---
@app.get("/hello")
def hello_world():
    """
    简单 GET 路由

    Express: app.get("/hello", (req, res) => res.json({ message: "Hello, World!" }))
    """
    return {"message": "Hello, World!"}


# --- 2b. 路径参数（Path Parameters）---
@app.get("/hello/{name}")
def hello_name(name: str):
    """
    带路径参数的 GET 路由

    Express: app.get("/hello/:name", (req, res) => {
        res.json({ message: `Hello, ${req.params.name}!` })
    })

    FastAPI 自动把 {name} 映射到函数参数 name
    类型标注 name: str 自动校验 + 文档生成
    """
    return {"message": f"Hello, {name}!"}


# --- 2c. 查询参数（Query Parameters）---
@app.get("/search")
def search(
    q: str,                                    # 必填 query 参数 — ?q=xxx
    page: int = 1,                             # 可选，默认 1 — &page=2
    limit: int = Query(default=10, le=100),    # 可选，最大 100 — &limit=20
):
    """
    查询参数示例

    Express: app.get("/search", (req, res) => {
        const { q, page = 1, limit = 10 } = req.query
        // 手动校验 limit <= 100 ...
    })

    FastAPI 自动做了：
    1. q 没有默认值 → 必填参数，缺少返回 422 错误
    2. page: int = 1 → 可选参数，自动转 int
    3. Query(le=100) → 额外约束校验（le = less than or equal）
    """
    return {
        "query": q,
        "page": page,
        "limit": limit,
        "results": f"搜索 '{q}' 的结果（第 {page} 页，每页 {limit} 条）",
    }


# 测试代码（取消注释后运行）：
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run("week3-rag-and-fastapi.04_fastapi_basics:app", host="0.0.0.0", port=8000, reload=True)
#
# 然后测试：
# curl http://localhost:8000/hello
# curl http://localhost:8000/hello/张三
# curl "http://localhost:8000/search?q=RAG&page=1&limit=5"
# curl "http://localhost:8000/search"  ← 会返回 422 错误（缺少 q 参数）


# ===========================================
# 3. 请求体 + Pydantic — POST 请求
# ===========================================
# Express 写法（需要额外安装 Zod）：
#   const { z } = require('zod')
#   const schema = z.object({
#       title: z.string().min(1).max(100),
#       content: z.string(),
#       tags: z.array(z.string()).optional()
#   })
#   app.post("/articles", (req, res) => {
#       const result = schema.safeParse(req.body)
#       if (!result.success) return res.status(422).json(result.error)
#       // ... 处理逻辑
#   })
#
# FastAPI 写法（Pydantic 是内置的！第二周学过的 Pydantic 直接用）：
#   class Article(BaseModel):
#       title: str = Field(min_length=1, max_length=100)
#       content: str
#       tags: list[str] = []
#
#   @app.post("/articles")
#   def create_article(article: Article):
#       return {"id": 1, **article.model_dump()}
#
# 关键区别：
# - Express 需要 express.json() 中间件解析 body + Zod 校验
# - FastAPI 自动解析 JSON body + Pydantic 自动校验
# - 校验失败自动返回 422 错误（包含详细的错误信息）

from pydantic import BaseModel, Field
from typing import Optional

# --- 请求体模型 ---
class ArticleCreate(BaseModel):
    """
    文章创建请求模型

    第二周学过 Pydantic，这里直接用！
    在 FastAPI 中，Pydantic 模型 = 请求体 schema + 自动校验 + 文档生成
    """
    title: str = Field(min_length=1, max_length=100, description="文章标题")
    content: str = Field(min_length=1, description="文章内容")
    tags: list[str] = Field(default=[], description="标签列表")

# --- POST 路由 ---
@app.post("/articles")
def create_article(article: ArticleCreate):
    """
    创建文章

    Express 等价：
    app.post("/articles", (req, res) => {
        const validated = schema.parse(req.body)  // Zod 校验
        res.status(201).json({ id: 1, ...validated })
    })

    FastAPI 自动做了：
    1. 解析 JSON body → ArticleCreate 实例
    2. 校验每个字段（title 长度、content 不为空等）
    3. 校验失败 → 自动返回 422 + 详细错误信息
    4. 校验通过 → article 参数是类型安全的 Pydantic 对象
    """
    # article.title, article.content, article.tags 都是类型安全的
    return {
        "id": 1,
        "status": "created",
        **article.model_dump(),  # Pydantic v2 的 model_dump() = v1 的 .dict()
    }

# # 测试:
# # curl -X POST http://localhost:8000/articles \
# #   -H "Content-Type: application/json" \
# #   -d '{"title": "RAG 入门", "content": "RAG 是检索增强生成...", "tags": ["AI", "RAG"]}'
# #
# # 故意发送无效数据（体验自动 422 校验）：
# # curl -X POST http://localhost:8000/articles \
# #   -H "Content-Type: application/json" \
# #   -d '{"title": "", "content": ""}'
# #   → 自动返回 422 + {"detail": [{"msg": "String should have at least 1 character", ...}]}


# ===========================================
# 4. 响应模型 — 控制 API 返回格式
# ===========================================
# Express 写法：
#   app.get("/articles/:id", (req, res) => {
#       const article = db.find(req.params.id)
#       // 手动挑选要返回的字段（防止泄露敏感数据）
#       res.json({ id: article.id, title: article.title })
#   })
#
# FastAPI 写法 — 用 response_model 自动过滤字段：
#   @app.get("/articles/{id}", response_model=ArticleResponse)
#   def get_article(id: int):
#       return full_article_object  # FastAPI 自动只返回 ArticleResponse 中定义的字段
#
# response_model 三大好处：
# 1. 自动过滤 — 只返回模型定义的字段，防止泄露密码等敏感数据
# 2. 自动序列化 — datetime → string, Enum → value
# 3. 文档生成 — /docs 显示精确的响应 schema

# --- 响应模型 ---
class ArticleResponse(BaseModel):
    """文章响应模型 — 只返回前端需要的字段"""
    id: int
    title: str
    content: str
    tags: list[str] = []

class ArticleDetail(ArticleResponse):
    """文章详情 — 继承基础响应，添加额外字段"""
    author: str = "anonymous"
    created_at: str = "2024-01-01"

# --- 模拟数据库 ---
fake_db = {
    1: {
        "id": 1,
        "title": "RAG 入门",
        "content": "RAG 是检索增强生成...",
        "tags": ["AI", "RAG"],
        "author": "张三",
        "created_at": "2024-03-15",
        "password_hash": "abc123secret",  # 敏感数据！不应返回给前端
    }
}

@app.get("/articles/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int):
    """
    获取文章详情

    Express 等价（需要手动过滤字段）：
    app.get("/articles/:id", (req, res) => {
        const article = db[req.params.id]
        const { password_hash, ...safe } = article  // 手动排除敏感字段
        res.json(safe)
    })

    FastAPI 的 response_model 自动过滤！
    即使 fake_db 里有 password_hash，返回时会被自动移除
    因为 ArticleDetail 模型中没有定义 password_hash 字段
    """
    if article_id not in fake_db:
        # 类似 Express 的 res.status(404).json(...)
        return JSONResponse(status_code=404, content={"error": "文章不存在"})
    return fake_db[article_id]  # 返回完整 dict，FastAPI 自动按 response_model 过滤


# ===========================================
# 5. RAG 接口 — 把 RAG 变成 API
# ===========================================
# 这是本周的核心：把 Day 1 学的 RAG 流程包装成 HTTP API
# 前端通过 fetch 调用 → 后端做 RAG → 返回 AI 回答 + 来源
#
# 两个端点：
# POST /index — 索引文档（把文档存入向量库）
# POST /ask   — 提问（检索 + AI 回答）
#
# JS 前端调用示例：
# const res = await fetch("/ask", {
#     method: "POST",
#     headers: { "Content-Type": "application/json" },
#     body: JSON.stringify({ question: "什么是 RAG？" })
# })
# const data = await res.json()
# console.log(data.answer, data.sources)

import chromadb

# 初始化向量库（内存模式，重启会丢失）
chroma_client = chromadb.Client()
# get_or_create 防止重复创建报错
collection = chroma_client.get_or_create_collection(name="rag_docs")

# 初始化 AI 客户端
ai_client, AI_MODEL = get_client(Path(__file__).parent / ".env")

# --- 请求/响应模型 ---
class IndexRequest(BaseModel):
    """索引请求 — 把一篇文档存入向量库"""
    text: str = Field(description="文档内容")
    source: str = Field(default="unknown", description="文档来源（文件名等）")
    chunk_size: int = Field(default=300, ge=50, le=2000, description="分块大小")

class IndexResponse(BaseModel):
    """索引响应"""
    message: str
    chunks_count: int
    source: str

class AskRequest(BaseModel):
    """提问请求"""
    question: str = Field(min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="检索结果数量")

class AskResponse(BaseModel):
    """提问响应 — 包含 AI 回答和来源"""
    answer: str
    sources: list[dict]
    question: str


# --- 统一响应格式 ---
def success(data=None, msg="success"):
    """成功响应 — {"code": 0, "msg": "success", "data": ...}"""
    return {"code": 0, "msg": msg, "data": data}

def error(code=500, msg="服务器错误", data=None):
    """错误响应 — {"code": 500, "msg": "...", "data": null}"""
    return {"code": code, "msg": msg, "data": data}

# --- 文档索引端点 ---
@app.post("/index", response_model=IndexResponse)
def index_document(req: IndexRequest):
    """
    索引文档 — 把文本分块后存入向量库

    流程：
    1. 收到文本 → 按段落分块
    2. 每个块存入 ChromaDB（自动 embedding）
    3. 返回分块数量

    JS 前端调用：
    await fetch("/index", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            text: "你的文档内容...",
            source: "readme.md"
        })
    })
    """
    # 按段落分块
    paragraphs = [p.strip() for p in req.text.split("\n\n") if p.strip() and len(p.strip()) > 20]

    if not paragraphs:
        # 如果没有段落分隔，按固定大小分块
        paragraphs = []
        for i in range(0, len(req.text), req.chunk_size):
            chunk = req.text[i:i + req.chunk_size].strip()
            if chunk:
                paragraphs.append(chunk)

    if not paragraphs:
        return JSONResponse(status_code=400, content={"error": "文档内容太短或为空"})

    # 生成唯一 ID（防止重复添加）
    import hashlib
    base_id = hashlib.md5(req.source.encode()).hexdigest()[:8]
    ids = [f"{base_id}_{i}" for i in range(len(paragraphs))]
    metadatas = [{"source": req.source, "chunk_index": i} for i in range(len(paragraphs))]

    # 存入向量库（Chroma 自动做 embedding）
    collection.upsert(
        documents=paragraphs,
        ids=ids,
        metadatas=metadatas,
    )

    return IndexResponse(
        message=f"文档 '{req.source}' 索引成功",
        chunks_count=len(paragraphs),
        source=req.source,
    )

# --- RAG 提问端点 ---
@app.post("/ask")
def ask_question(req: AskRequest):
    """
    RAG 提问 — 检索相关文档 + AI 生成回答

    流程：
    1. 用户问题 → ChromaDB 检索 top_k 个相关文档块
    2. 把检索结果拼接成 context
    3. 构造 RAG prompt → 调 AI 生成回答
    4. 返回统一格式 {"code": 0, "msg": "success", "data": {...}}

    JS 前端调用：
    const { code, msg, data } = await fetch("/ask", {
        method: "POST",
        body: JSON.stringify({ question: "什么是 RAG？", top_k: 3 })
    }).then(r => r.json())
    """
    # 检查向量库是否有数据
    if collection.count() == 0:
        return error(code=400, msg="向量库为空，请先通过 /index 接口添加文档")

    # Step 1: 检索相关文档
    results = collection.query(
        query_texts=[req.question],
        n_results=min(req.top_k, collection.count()),
    )

    # Step 2: 拼接 context
    context_parts = []
    sources = []
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        context_parts.append(f"[片段 {i+1}] {doc}")
        sources.append({
            "content": doc[:200],
            "source": meta.get("source", "unknown"),
            "relevance": round(1 / (1 + dist), 4),  # 距离转相关度
        })

    context = "\n\n".join(context_parts)

    # Step 3: 构造 RAG prompt
    rag_prompt = f"""根据以下参考文档回答用户的问题。
规则：
1. 只基于提供的文档内容回答
2. 如果文档中没有相关信息，明确说"根据现有文档无法回答"
3. 回答时引用文档中的具体内容

参考文档：
{context}

用户问题：{req.question}"""

    # Step 4: 调 AI 生成回答
    answer = ask(ai_client, AI_MODEL, rag_prompt, max_tokens=1000)

    return success(data={
        "answer": answer,
        "sources": sources,
        "question": req.question,
    })


# ===========================================
# 6. SSE 流式输出 — 打字机效果
# ===========================================
# 前端 ChatGPT 那种逐字输出的效果就是 SSE（Server-Sent Events）
#
# Express 写法：
#   app.get("/stream", (req, res) => {
#       res.setHeader("Content-Type", "text/event-stream")
#       res.setHeader("Cache-Control", "no-cache")
#       res.write("data: 第一段\n\n")
#       res.write("data: 第二段\n\n")
#       res.end()
#   })
#
# FastAPI 写法 — 用 async generator + StreamingResponse 或 sse-starlette：
#   from sse_starlette.sse import EventSourceResponse
#
#   @app.get("/stream")
#   async def stream():
#       async def generate():
#           yield {"data": "第一段"}
#           yield {"data": "第二段"}
#       return EventSourceResponse(generate())
#
# SSE vs WebSocket：
# - SSE = 单向（服务器→客户端），适合 AI 流式输出
# - WebSocket = 双向，适合聊天室、游戏
# - SSE 更简单，HTTP 协议原生支持，不需要额外握手

import asyncio
from fastapi.responses import StreamingResponse

# --- 方法 1: 使用 StreamingResponse（FastAPI 内置）---
@app.post("/stream/basic")
async def stream_basic():
    """
    基础流式输出 — 使用 FastAPI 内置的 StreamingResponse

    Express 等价：
    app.post("/stream/basic", (req, res) => {
        res.setHeader("Content-Type", "text/event-stream")
        res.setHeader("Cache-Control", "no-cache")
        // 逐段发送
        for (const chunk of chunks) {
            res.write(`data: ${JSON.stringify({ text: chunk })}\n\n`)
        }
        res.end()
    })
    """
    async def generate():
        """
        async generator — Python 的异步生成器

        JS 类比：
        async function* generate() {
            yield "data: chunk1\n\n"
            yield "data: chunk2\n\n"
        }
        """
        # 模拟 AI 流式输出（实际项目中用 client.messages.stream()）
        chunks = ["RAG ", "是检索", "增强生成", "的缩写，", "它让 AI ", "先查资料", "再回答。"]
        for chunk in chunks:
            # SSE 格式：每条消息以 "data: " 开头，以 "\n\n" 结尾
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.3)  # 模拟延迟
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

# --- 方法 2: 使用 sse-starlette（更标准的 SSE）---
from sse_starlette.sse import EventSourceResponse

@app.post("/stream/sse")
async def stream_sse():
    """
    标准 SSE 输出 — 使用 sse-starlette 库

    sse-starlette 自动处理：
    1. Content-Type 头
    2. 心跳保活（防止连接超时）
    3. 标准 SSE 格式
    """
    async def generate():
        # 实际项目中，这里调用 AI 的流式 API
        # 例如：
        # stream = client.messages.stream(
        #     model=MODEL,
        #     messages=[{"role": "user", "content": req.question}],
        #     max_tokens=500,
        # )
        # async for text in stream.text_stream:
        #     yield {"event": "message", "data": text}

        # 这里用模拟数据演示
        answer_parts = ["根据文档，", "RAG（检索增强生成）", "是一种让 AI ", "先从知识库检索相关信息，",
                        "再基于检索结果", "生成回答的技术。"]
        for part in answer_parts:
            yield {"event": "message", "data": part}
            await asyncio.sleep(0.3)
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(generate())

# 前端 JS 消费 SSE 的代码：
# const evtSource = new EventSource("/stream/basic")
# evtSource.onmessage = (e) => {
#     if (e.data === "[DONE]") { evtSource.close(); return }
#     document.getElementById("output").textContent += e.data
# }
#
# 或者用 fetch + ReadableStream（更灵活）：
# const response = await fetch("/stream/basic", { method: "POST", body: ... })
# const reader = response.body.getReader()
# const decoder = new TextDecoder()
# while (true) {
#     const { done, value } = await reader.read()
#     if (done) break
#     const text = decoder.decode(value)
#     // 解析 SSE 格式
# }


# ===========================================
# 7. CORS + 静态文件 — 前后端联调必备
# ===========================================
# 前端工程师最熟悉的问题：跨域！
#
# Express 写法：
#   const cors = require('cors')
#   app.use(cors({ origin: "http://localhost:3000" }))
#   app.use(express.static("public"))
#
# FastAPI 写法：
#   from fastapi.middleware.cors import CORSMiddleware
#   app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])
#   app.mount("/static", StaticFiles(directory="public"), name="static")
#
# 完全一样的思路，只是语法不同

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- CORS 中间件 ---
# Express: app.use(cors({ origin: [...], methods: [...] }))
app.add_middleware(
    CORSMiddleware,
    # 允许的前端域名列表
    # 开发环境可以用 ["*"] 允许所有，生产环境要限制
    allow_origins=[
        "http://localhost:3000",   # React 默认端口
        "http://localhost:5173",   # Vite 默认端口
        "http://localhost:8080",   # Vue CLI 默认端口
    ],
    allow_credentials=True,        # 允许 cookie
    allow_methods=["*"],           # 允许所有 HTTP 方法
    allow_headers=["*"],           # 允许所有请求头
)

# --- 静态文件 ---
# 先确保 static 目录存在
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Express: app.use("/static", express.static("static"))
# FastAPI: app.mount("/static", StaticFiles(directory="static"), name="static")
#
# 注意：mount 必须放在路由定义之后（或者路径不冲突）
# 访问 http://localhost:8000/static/index.html 就能打开静态文件
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

print("CORS 已配置 — 允许来自 localhost:3000/5173/8080 的前端请求")
print("静态文件已挂载 — /static 目录")
print()

# --- 额外：错误处理中间件 ---
# Express: app.use((err, req, res, next) => { res.status(500).json({ error: err.message }) })
# FastAPI: 用 exception_handler

from fastapi import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    全局 HTTP 异常处理器 — 统一返回 {code, msg, data}

    Express 等价：
    app.use((err, req, res, next) => {
        res.status(err.status || 500).json({ code: err.status, msg: err.message, data: null })
    })
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=error(code=exc.status_code, msg=exc.detail),
    )

from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """捕获 Pydantic 422 校验错误"""
    return JSONResponse(
        status_code=422,
        content=error(code=422, msg="参数校验失败", data=exc.errors()),
    )


# ===========================================
# 总结
# ===========================================
print("=== Day 4 总结 ===\n")
print("Express → FastAPI 速查：")
print("  app.get('/path', handler)     → @app.get('/path')")
print("  app.post('/path', handler)    → @app.post('/path')")
print("  req.params.id                 → 函数参数 (path param)")
print("  req.query.page                → 函数参数 + 默认值 (query param)")
print("  req.body + Zod               → Pydantic Model 参数")
print("  res.json({...})               → return {...}")
print("  res.status(201).json(...)     → JSONResponse(status_code=201, ...)")
print("  app.use(cors())               → app.add_middleware(CORSMiddleware, ...)")
print("  app.use(express.static(...))  → app.mount('/static', StaticFiles(...))")
print("  res.write() / SSE             → StreamingResponse / EventSourceResponse")
print()
print("启动命令（在项目根目录运行）：")
print("  uvicorn week3-rag-and-fastapi.04_fastapi_basics:app --reload")
print()
print("启动后访问：")
print("  http://localhost:8000/docs  → API 文档（自动生成的 Swagger UI！）")


# ===========================================
# 启动服务器
# ===========================================
# 取消下面的注释来启动服务器
# 但更推荐用命令行启动（支持热重载）：
#   uvicorn week3-rag-and-fastapi.04_fastapi_basics:app --reload

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" 允许局域网访问（类似 Express 的 app.listen(8000, "0.0.0.0")）
    # reload=True 文件变动自动重启（类似 nodemon）
    uvicorn.run(
        "week3-rag-and-fastapi.04_fastapi_basics:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
