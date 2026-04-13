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

# TODO 1.1: 创建 FastAPI 应用，设置 title, version
app = FastAPI(
    # TODO: 设置 title, description, version
)


# TODO 1.2: 实现 GET / 路由，返回 {"message": "Hello, Week3!", "status": "ok"}
@app.get("/")
def root():
    # TODO: 实现
    pass


# TODO 1.3: 实现 GET /health 路由，返回 {"status": "healthy", "version": "1.0.0"}
# TODO: 用 @app.get("/health") 装饰器


# --- 题目 2: GET 路由参数 ---

# TODO 2.1: 实现 GET /users/{user_id}
# 路径参数: user_id (int)
# 返回: {"user_id": 用户ID, "name": f"User_{用户ID}"}
@app.get("/users/{user_id}")
def get_user(user_id: int):
    # TODO: 实现
    pass


# TODO 2.2: 实现 GET /search 路由
# 查询参数: q (str, 必填), page (int, 默认1), limit (int, 默认20, 最大100)
# 返回: {"query": q, "page": page, "limit": limit, "results": f"找到 {limit} 条结果"}
@app.get("/search")
def search(
    q: str,
    page: int = 1,
    limit: int = Query(default=20, le=100),
):
    # TODO: 实现（函数签名已经给了，返回即可）
    pass


# --- 题目 3: POST + Pydantic 请求体 ---

# TODO 3.1: 定义 TaskCreate 模型
# 字段: title (str, min_length=1), description (str, 默认""), priority (int, ge=1, le=5, 默认3)
class TaskCreate(BaseModel):
    # TODO: 定义字段
    pass


# TODO 3.2: 实现 POST /tasks 路由
# 接收 TaskCreate 请求体
# 返回: {"id": 1, "status": "created", ...任务数据}
fake_tasks = []

@app.post("/tasks")
def create_task(task: TaskCreate):
    # TODO: 把 task 加入 fake_tasks，返回结果
    # 返回格式: {"id": 1, "status": "created", "title": task.title, ...}
    pass


# --- 题目 4: 响应模型 ---

# TODO 4.1: 定义 TaskResponse 模型
# 字段: id (int), title (str), description (str), priority (int)
class TaskResponse(BaseModel):
    # TODO: 定义
    pass


# TODO 4.2: 实现 GET /tasks/{task_id} 路由
# 设置 response_model=TaskResponse
# 如果 task_id 不存在，返回 404
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    # TODO: 从 fake_tasks 中查找，找不到返回 HTTPException(status_code=404, detail="任务不存在")
    pass


# --- 题目 5: RAG 接口设计 ---

# TODO 5.1: 设计 RAG API 的请求/响应模型
class RAGRequest(BaseModel):
    # TODO: question (str, min_length=1), top_k (int, 默认3, ge=1, le=10)
    pass

class RAGResponse(BaseModel):
    # TODO: answer (str), sources (list[dict]), question (str)
    pass


# TODO 5.2: 实现 POST /rag/ask 路由（伪代码即可）
# 流程：
# 1. 收到 RAGRequest
# 2. 在 Chroma 中检索 question → top_k
# 3. 拼接 context
# 4. 构造 RAG prompt → 调 LLM
# 5. 返回 RAGResponse(answer=..., sources=..., question=...)
#
# 提示：实际实现需要初始化 chromadb.Client 和 AI client
# 这里只需要写路由函数骨架
#
# @app.post("/rag/ask", response_model=RAGResponse)
# def rag_ask(req: RAGRequest):
#     # TODO: 实现 RAG 流程
#     pass


# --- 题目 6: 错误处理 ---

# TODO 6.1: 实现全局 HTTP 异常处理器
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    全局异常处理
    返回格式: {"error": 错误信息, "status_code": 状态码}
    """
    # TODO: 实现
    pass


# --- 启动命令 ---
# 取消下面的注释来启动
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)

# 推荐用命令行：
# uvicorn practice_04_fastapi:app --reload --port 8000
