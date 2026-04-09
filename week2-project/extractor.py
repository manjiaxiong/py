# ===========================================
# extractor.py — 简历结构化提取
# ===========================================
# 用 Tool Use 从简历文本中提取结构化信息
# 用 Pydantic 模型校验提取结果
#
# 复习：
# - Day 2: Tool Use（AI 返回结构化数据）
# - Day 2: Pydantic（数据校验）
# - utils.py: get_client, clean_markdown
#
# JS 类比：
# Tool Use = 让 AI 调一个"提取函数"，返回 JSON
# Pydantic = Zod schema 校验
# ===========================================

import sys
import json
import time
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import get_client, clean_markdown
from logger import log_request


# ===========================================
# 1. Pydantic 模型 — 定义简历数据结构
# ===========================================

class ResumeInfo(BaseModel):
    """简历提取结果"""
    name: str = Field(description="姓名")
    years: int = Field(description="工作年限")
    skills: List[str] = Field(description="技能列表")
    education: str = Field(description="学历，如 本科、硕士、博士")
    expected_salary: Optional[str] = Field(default=None, description="期望薪资，如 20k-30k")


# ===========================================
# 2. Tool Use 定义 — 告诉 AI 用这个工具提取
# ===========================================

EXTRACT_TOOL = {
    "name": "extract_resume",
    "description": "从简历文本中提取结构化信息。必须使用此工具返回提取结果。",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "姓名",
            },
            "years": {
                "type": "integer",
                "description": "工作年限（整数）",
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "技能列表",
            },
            "education": {
                "type": "string",
                "description": "学历，如 本科、硕士、博士",
            },
            "expected_salary": {
                "type": "string",
                "description": "期望薪资，如 20k-30k。如果简历没提到，填 null",
            },
        },
        "required": ["name", "years", "skills", "education"],
    },
}


# ===========================================
# 3. 提取函数 — 调 API + 校验
# ===========================================

def extract_resume(resume_text: str) -> dict:
    """
    从简历文本中提取结构化信息

    流程：
    1. 调 API（带 Tool Use）→ AI 返回结构化 JSON
    2. 用 Pydantic 校验数据
    3. 返回校验后的 dict

    参数:
        resume_text: 简历文本

    返回:
        {"success": True, "data": {...}} 或 {"success": False, "error": "..."}
    """
    client, model = get_client(Path(__file__).parent / ".env")

    system = "你是一个简历解析助手。分析用户提供的简历文本，使用 extract_resume 工具提取结构化信息。"

    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": f"请提取这份简历的信息：\n\n{resume_text}"}],
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": "extract_resume"},
    )
    duration = time.time() - start

    # 从 tool_use block 中拿到结构化数据
    tool_input = None
    for block in response.content:
        if block.type == "tool_use":
            tool_input = block.input
            break

    if tool_input is None:
        return {"success": False, "error": "AI 没有调用提取工具"}

    # 记录日志
    log_request(
        prompt=resume_text,
        response=json.dumps(tool_input, ensure_ascii=False),
        tokens={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
        duration=duration,
        extra={"model": model, "task": "extract_resume"},
    )

    # 用 Pydantic 校验
    try:
        info = ResumeInfo(**tool_input)
        return {"success": True, "data": info.model_dump()}
    except ValidationError as e:
        return {"success": False, "error": f"数据校验失败: {e}"}


# ===========================================
# 测试
# ===========================================
if __name__ == "__main__":
    test_resume = """
    张三，5年前端开发经验，熟练掌握 React、TypeScript、Node.js。
    本科毕业于浙江大学计算机系。期望薪资 25k-35k。
    """
    result = extract_resume(test_resume)
    print(json.dumps(result, ensure_ascii=False, indent=2))
