# ===========================================
# main.py — AI Workflow Assistant FastAPI 入口
# ===========================================
# FastAPI + LangGraph + SSE 流式进度
# 用法: uvicorn week4-project.main:app --reload
# ===========================================

import sys
import json
import time
import uuid
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from models import TaskSubmitRequest, TaskStatusResponse, StepInfo, HealthResponse
from tools import TOOLS
import workflow

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("main")

# --- FastAPI 应用 ---
app = FastAPI(
    title="AI Workflow Assistant",
    description="第 4 周毕业项目 — LangGraph 工作流助手",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 任务存储（内存）
tasks = {}


# --- 统一响应格式 ---

def success(data=None, msg="success"):
    return {"code": 0, "msg": msg, "data": data}


def error(code=500, msg="服务器错误", data=None):
    return {"code": code, "msg": msg, "data": data}


# --- 启动事件 ---

@app.on_event("startup")
async def startup():
    """初始化 workflow"""
    logger.info("初始化 AI Workflow...")
    workflow.init(Path(__file__).parent / ".env")
    logger.info(f"可用工具: {list(TOOLS.keys())}")
    logger.info("AI Workflow Assistant 启动完成")


# --- 日志中间件 ---

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    logger.info(json.dumps({
        "method": request.method,
        "path": str(request.url.path),
        "status": response.status_code,
        "latency_ms": round(latency * 1000, 1),
    }))
    return response


# --- 路由 ---

@app.get("/", response_class=HTMLResponse)
async def index():
    """前端页面"""
    html_path = Path(__file__).parent / "templates" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AI Workflow Assistant</h1><p>templates/index.html 不存在</p>")


@app.get("/api/health")
async def health():
    """健康检查"""
    return success(data={
        "status": "healthy",
        "version": "1.0.0",
        "tools_count": len(TOOLS),
    })


@app.post("/api/submit")
async def submit_task(req: TaskSubmitRequest):
    """提交任务"""
    task_id = str(uuid.uuid4())[:8]

    tasks[task_id] = {
        "task_id": task_id,
        "task_description": req.task_description,
        "max_steps": req.max_steps,
        "status": "pending",
        "steps": [],
        "final_result": None,
    }

    logger.info(f"任务提交: {task_id} — {req.task_description[:50]}")

    # 同步执行工作流
    try:
        tasks[task_id]["status"] = "running"
        result = workflow.run_task(req.task_description, max_steps=req.max_steps)

        # 更新任务状态
        steps = []
        for r in result.get("step_results", []):
            steps.append(StepInfo(
                step_number=r["step"],
                description=r.get("description", ""),
                tool_used=r.get("tool", ""),
                tool_input=str(r.get("input", ""))[:200],
                tool_output=str(r.get("output", ""))[:500],
                status=r.get("status", "success"),
                latency_ms=r.get("latency_ms", 0),
            ))

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["steps"] = steps
        tasks[task_id]["final_result"] = result.get("final_result", "")

        return success(data={
            "task_id": task_id,
            "status": "completed",
            "steps": [s.model_dump() for s in steps],
            "final_result": result.get("final_result", ""),
        })

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["final_result"] = str(e)
        logger.error(f"任务失败: {task_id} — {e}")
        return error(code=500, msg=f"任务执行失败: {e}")


@app.get("/api/status/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    if task_id not in tasks:
        return error(code=404, msg="任务不存在")

    task = tasks[task_id]
    return success(data=task)


@app.get("/api/stream/{task_id}")
async def stream_task(task_id: str):
    """SSE 流式返回任务进度"""
    if task_id not in tasks:
        return error(code=404, msg="任务不存在")

    async def event_generator():
        task = tasks[task_id]

        # 发送任务信息
        yield {"event": "task_start", "data": json.dumps({
            "task_id": task_id,
            "description": task["task_description"],
        }, ensure_ascii=False)}

        # 发送已有的步骤
        for step in task.get("steps", []):
            yield {"event": "step_result", "data": json.dumps(
                step.model_dump() if hasattr(step, "model_dump") else step,
                ensure_ascii=False,
            )}
            await asyncio.sleep(0.1)

        # 发送最终结果
        if task.get("final_result"):
            yield {"event": "done", "data": json.dumps({
                "final_result": task["final_result"],
                "status": task["status"],
            }, ensure_ascii=False)}

    return EventSourceResponse(event_generator())


# --- 异常处理 ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=error(code=exc.status_code, msg=exc.detail),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"未处理异常: {exc}")
    return JSONResponse(
        status_code=500,
        content=error(code=500, msg="服务器内部错误"),
    )


# --- 启动 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
