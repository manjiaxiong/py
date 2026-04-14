# ===========================================
# 练习 4：FastAPI 后端（对应 Day 4）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 04_fastapi_basics.py / 04_fastapi_basics.md
# ===========================================

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional


# --- 题目 1: 第一个 FastAPI 应用 ---

# 创建 FastAPI 应用，设置 title, version
app = FastAPI(
    title="Week3 Practice API",
    description="练习 4：FastAPI 后端练习",
    version="1.0.0",
)


# 实现 GET / 路由，返回 {"message": "Hello, Week3!", "status": "ok"}
@app.get("/")
def root():
    return {"message": "Hello, Week3!", "status": "ok"}


# 实现 GET /health 路由，返回 {"status": "healthy", "version": "1.0.0"}
@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


# --- 题目 2: GET 路由参数 ---

# 实现 GET /users/{user_id}
# 路径参数: user_id (int)
# 返回: {"user_id": 用户ID, "name": f"User_{用户ID}"}
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User_{user_id}"}


# 实现 GET /search 路由
# 查询参数: q (str, 必填), page (int, 默认1), limit (int, 默认20, 最大100)
@app.get("/search")
def search(
    q: str,
    page: int = 1,
    limit: int = Query(default=20, le=100),
):
    return {"query": q, "page": page, "limit": limit, "results": f"找到 {limit} 条结果"}


# --- 题目 3: POST + Pydantic 请求体 ---

# 定义 TaskCreate 模型
# 字段: title (str, min_length=1), description (str, 默认""), priority (int, ge=1, le=5, 默认3)
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, description="任务标题")
    description: str = Field(default="", description="任务描述")
    priority: int = Field(default=3, ge=1, le=5, description="优先级 1-5")


# 实现 POST /tasks 路由
# 接收 TaskCreate 请求体
# 返回: {"id": 1, "status": "created", ...任务数据}
fake_tasks = []

@app.post("/tasks")
def create_task(task: TaskCreate):
    new_task = {
        "id": len(fake_tasks) + 1,
        "status": "created",
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
    }
    fake_tasks.append(new_task)
    return new_task


# --- 题目 4: 响应模型 ---

# 定义 TaskResponse 模型
# 字段: id (int), title (str), description (str), priority (int)
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int


# 实现 GET /tasks/{task_id} 路由
# 设置 response_model=TaskResponse
# 如果 task_id 不存在，返回 404
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    for task in fake_tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="任务不存在")


# --- 题目 5: RAG 接口设计 ---

# 设计 RAG API 的请求/响应模型
class RAGRequest(BaseModel):
    question: str = Field(min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="检索结果数量")

class RAGResponse(BaseModel):
    answer: str
    sources: list[dict]
    question: str


# 实现 POST /rag/ask 路由（伪代码即可，实际实现需要 RAG 依赖）
@app.post("/rag/ask", response_model=RAGResponse)
def rag_ask(req: RAGRequest):
    """
    RAG 问答接口（骨架代码）

    实际流程：
    1. 收到 RAGRequest
    2. 在 Chroma 中检索 question → top_k
    3. 拼接 context
    4. 构造 RAG prompt → 调 LLM
    5. 返回 RAGResponse(answer=..., sources=..., question=...)
    """
    # 伪代码实现（没有实际 RAG 依赖时）
    # results = chroma_collection.query(query_texts=[req.question], n_results=req.top_k)
    # context = "\n\n".join(results["documents"][0])
    # answer = ask_ai_client(context, req.question)
    # sources = [{"source": m["source"]} for m in results["metadatas"][0]]

    return RAGResponse(
        answer="（骨架代码）此处需要接入实际的 RAG pipeline",
        sources=[{"source": "example.md", "distance": 0.5}],
        question=req.question,
    )


# --- 题目 6: 错误处理 ---

from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    全局异常处理
    返回格式: {"error": 错误信息, "status_code": 状态码}
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


# --- 启动命令 ---
# 取消下面的注释来启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)

# 推荐用命令行：
# uvicorn practice_04_fastapi:app --reload --port 8000
