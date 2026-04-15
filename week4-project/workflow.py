# ===========================================
# workflow.py — LangGraph 工作流定义
# ===========================================
# 用 LangGraph 编排 Agent 工作流：
# parse_task → plan_steps → execute_loop → summarize → END
# ===========================================

import re
import json
import time
import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, END

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import get_client, ask
from tools import TOOLS, execute_tool, get_tool_descriptions

# AI 客户端（在 init 时设置）
_client = None
_model = None


def init(env_path=None):
    """初始化 AI 客户端"""
    global _client, _model
    _client, _model = get_client(env_path)
    return _client, _model


# --- State 定义 ---

class WorkflowState(TypedDict):
    task_description: str          # 用户任务描述
    plan: list                     # 执行计划 [{step, tool, input}]
    current_step: int              # 当前步骤索引
    step_results: list             # 每步执行结果
    final_result: str              # 最终结果
    status: str                    # 状态：planning / executing / done / error
    max_steps: int                 # 最大步骤数


# --- Node 定义 ---

def plan_node(state: WorkflowState) -> dict:
    """
    规划节点：根据任务生成执行计划

    让 LLM 把任务分解成多个步骤，每步指定工具
    """
    tool_desc = get_tool_descriptions()

    prompt = f"""你是一个任务规划助手。根据用户任务，生成一个执行计划。

可用工具：
{tool_desc}

请用 JSON 数组格式返回计划，每个步骤包含：
- step: 步骤序号
- description: 步骤描述
- tool: 工具名（必须从上面的工具中选）
- input: 工具输入

限制：最多 {state['max_steps']} 个步骤。

用户任务：{state['task_description']}

返回纯 JSON 数组，不要其他内容："""

    response = ask(_client, _model, prompt, max_tokens=800)

    # 解析 JSON
    try:
        # 清理 markdown 代码块标记
        raw = response.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0].strip()
        plan = json.loads(raw)
        if not isinstance(plan, list):
            plan = [plan]
    except json.JSONDecodeError:
        # 解析失败，生成默认计划
        plan = [
            {"step": 1, "description": "搜索相关信息", "tool": "web_search", "input": state["task_description"]},
            {"step": 2, "description": "总结结果", "tool": "text_summarize", "input": "搜索结果"},
        ]

    # 限制步骤数
    plan = plan[:state["max_steps"]]

    return {"plan": plan, "status": "planned", "current_step": 0}


def execute_node(state: WorkflowState) -> dict:
    """
    执行节点：执行当前步骤
    """
    idx = state["current_step"]
    plan = state["plan"]
    results = list(state.get("step_results", []))

    if idx >= len(plan):
        return {"status": "all_done"}

    step = plan[idx]
    tool_name = step.get("tool", "web_search")
    tool_input = step.get("input", "")

    # 如果 input 引用了上一步结果，替换
    if results and "搜索结果" in str(tool_input):
        prev_output = results[-1].get("output", "")
        tool_input = prev_output[:500]

    # 执行
    start = time.time()
    result = execute_tool(tool_name, tool_input)
    latency = time.time() - start

    results.append({
        "step": idx + 1,
        "description": step.get("description", ""),
        "tool": tool_name,
        "input": tool_input[:200],
        "output": str(result.get("output", ""))[:500],
        "status": result.get("status", "success"),
        "latency_ms": round(latency * 1000, 1),
    })

    return {
        "step_results": results,
        "current_step": idx + 1,
        "status": "executing",
    }


def should_continue(state: WorkflowState) -> str:
    """判断是否继续执行下一步"""
    if state["current_step"] >= len(state["plan"]):
        return "summarize"
    return "execute"


def summarize_node(state: WorkflowState) -> dict:
    """
    总结节点：汇总所有步骤结果，生成最终回答
    """
    # 收集所有步骤结果
    step_summary = ""
    for r in state.get("step_results", []):
        step_summary += f"\n步骤 {r['step']}: {r['description']}\n"
        step_summary += f"  工具: {r['tool']}\n"
        step_summary += f"  结果: {r['output'][:200]}\n"

    prompt = f"""根据以下任务执行过程，给出最终答案：

任务：{state['task_description']}

执行过程：
{step_summary}

请简洁地总结最终结果："""

    final = ask(_client, _model, prompt, max_tokens=500)

    return {"final_result": final, "status": "completed"}


# --- 构建工作流图 ---

def build_workflow():
    """
    构建 LangGraph 工作流

    流程：plan → execute (loop) → summarize → END
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.add_node("summarize", summarize_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.add_conditional_edges(
        "execute",
        should_continue,
        {"execute": "execute", "summarize": "summarize"},
    )
    graph.add_edge("summarize", END)

    return graph.compile()


# 全局 workflow 实例
workflow_app = None


def get_workflow():
    """获取全局 workflow 实例"""
    global workflow_app
    if workflow_app is None:
        workflow_app = build_workflow()
    return workflow_app


def run_task(task_description, max_steps=5):
    """
    运行完整任务

    参数:
        task_description: 任务描述
        max_steps: 最大步骤数

    返回:
        WorkflowState（最终状态）
    """
    app = get_workflow()
    initial_state = {
        "task_description": task_description,
        "plan": [],
        "current_step": 0,
        "step_results": [],
        "final_result": "",
        "status": "start",
        "max_steps": max_steps,
    }
    return app.invoke(initial_state)


# --- 测试 ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
    init(Path(__file__).parent / ".env")

    print("=== Workflow 测试 ===\n")
    result = run_task("帮我查一下 Python 和 FastAPI 的关系，然后计算 3.14 * 2")

    print(f"\n状态: {result['status']}")
    print(f"计划步骤: {len(result['plan'])}")
    print(f"执行步骤: {len(result['step_results'])}")
    for r in result["step_results"]:
        print(f"  [{r['step']}] {r['tool']}: {str(r['output'])[:60]}...")
    print(f"\n最终结果:\n{result['final_result']}")
