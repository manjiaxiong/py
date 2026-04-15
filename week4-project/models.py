# ===========================================
# models.py — AI Workflow Assistant 数据模型
# ===========================================
# Pydantic 模型定义：请求体、响应体、内部状态
# ===========================================

from pydantic import BaseModel, Field
from typing import Optional


class TaskSubmitRequest(BaseModel):
    """提交任务请求"""
    task_description: str = Field(min_length=5, max_length=2000, description="任务描述")
    max_steps: int = Field(default=5, ge=1, le=10, description="最大步骤数")


class StepInfo(BaseModel):
    """单步执行信息"""
    step_number: int
    description: str
    tool_used: str
    tool_input: str
    tool_output: str
    status: str  # "running" | "success" | "error"
    latency_ms: float = 0


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str  # "pending" | "running" | "completed" | "error"
    task_description: str
    current_step: int = 0
    total_steps: int = 0
    steps: list[StepInfo] = []
    final_result: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    tools_count: int
