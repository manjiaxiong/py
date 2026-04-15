# ===========================================
# 练习 1：Agent 深入（对应 Day 1）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 01_agent_deep.py / 01_agent_deep.md
# ===========================================

import sys
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

client, MODEL = get_client(Path(__file__).parent / ".env")


# --- 题目 1: 工具注册表 ---

# TODO 1.1: 实现 3 个工具函数
def calculator(expression):
    """安全计算数学表达式"""
    try:
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expression):
            return str(eval(expression))
        return f"不支持的表达式: {expression}"
    except Exception as e:
        return f"计算错误: {e}"


def get_date(format_str=""):
    """获取当前日期"""
    now = datetime.now()
    return now.strftime(format_str if format_str else "%Y-%m-%d %H:%M:%S")


def search(query):
    """模拟搜索"""
    data = {
        "python": "Python 3.12 是最新稳定版，支持更好的错误提示。",
        "react": "React 18 支持并发渲染和 Suspense。",
        "docker": "Docker 是容器化平台，用于打包和部署应用。",
    }
    for key, val in data.items():
        if key in query.lower():
            return val
    return f"未找到 '{query}' 的相关信息"


# TODO 1.2: 把工具注册成 dict
TOOLS = {
    "calculator": {"fn": calculator, "description": "计算数学表达式"},
    "get_date": {"fn": get_date, "description": "获取当前日期时间"},
    "search": {"fn": search, "description": "搜索信息"},
}

print("=== 题目 1: 工具注册表 ===")
print(f"可用工具: {list(TOOLS.keys())}")
print(f"  calculator('2+3') = {calculator('2+3')}")
print(f"  get_date() = {get_date()}")
print(f"  search('python') = {search('python')[:50]}...")


# --- 题目 2: ReAct Prompt 设计 ---

# TODO 2.1: 写 ReAct 格式的 Prompt 模板
TOOL_DESC = "\n".join(f"- {n}: {t['description']}" for n, t in TOOLS.items())

REACT_PROMPT = """你是一个推理助手。你可以使用以下工具：

{tools}

请严格按照以下格式回答（每次只选一个工具）：

Thought: 分析当前情况
Action: 工具名
Action Input: 工具输入

当你有足够信息时：

Thought: 我有了最终答案
Final Answer: 你的最终答案

用户任务：{task}

{history}"""


# --- 题目 3: 解析 LLM 输出 ---

# TODO 3.1: 用正则从 LLM 回复中提取 Action/Input 或 Final Answer
def parse_response(response):
    """
    解析 ReAct 格式的 LLM 输出

    返回:
        {"type": "final", "answer": "..."} 或
        {"type": "action", "name": "...", "input": "..."} 或
        {"type": "unknown"}
    """
    final = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
    if final:
        return {"type": "final", "answer": final.group(1).strip()}

    action = re.search(r"Action:\s*(.+)", response)
    action_input = re.search(r"Action Input:\s*(.+)", response)
    if action:
        return {
            "type": "action",
            "name": action.group(1).strip(),
            "input": action_input.group(1).strip() if action_input else "",
        }

    return {"type": "unknown", "raw": response}


print("\n=== 题目 3: 解析 LLM 输出 ===")
# 测试解析
test_outputs = [
    "Thought: 需要计算\nAction: calculator\nAction Input: 2+3",
    "Thought: 我知道答案了\nFinal Answer: 结果是 5",
]
for out in test_outputs:
    parsed = parse_response(out)
    print(f"  输入: {out[:40]}... → {parsed['type']}")


# --- 题目 4: 带重试的工具调用 ---

# TODO 4.1: 实现带重试机制的工具执行
def execute_tool(tool_name, tool_input, max_retries=2):
    """调用工具，失败则重试"""
    if tool_name not in TOOLS:
        return f"工具 '{tool_name}' 不存在，可用: {list(TOOLS.keys())}"

    for attempt in range(max_retries):
        try:
            return TOOLS[tool_name]["fn"](tool_input)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️ 重试 {tool_name}（第 {attempt+1} 次）")
            else:
                return f"工具 {tool_name} 失败: {e}"


print("\n=== 题目 4: 工具调用 ===")
print(f"  calculator('10*5') = {execute_tool('calculator', '10*5')}")
print(f"  不存在工具 = {execute_tool('xxx', '')}")


# --- 题目 5: 完整 Agent Loop ---

# TODO 5.1: 实现完整的 Agent 循环
def agent_run(task, max_iterations=5):
    """
    运行 Agent 循环

    返回: {"answer": str, "steps": list, "iterations": int}
    """
    history = ""
    steps = []

    for i in range(max_iterations):
        prompt = REACT_PROMPT.format(tools=TOOL_DESC, task=task, history=history)
        response = ask(client, MODEL, prompt, max_tokens=500)
        parsed = parse_response(response)

        step = {"iteration": i + 1}

        if parsed["type"] == "final":
            step["type"] = "final"
            step["answer"] = parsed["answer"]
            steps.append(step)
            return {"answer": parsed["answer"], "steps": steps, "iterations": i + 1}

        elif parsed["type"] == "action":
            observation = execute_tool(parsed["name"], parsed["input"])
            step["type"] = "action"
            step["tool"] = parsed["name"]
            step["input"] = parsed["input"]
            step["observation"] = observation
            steps.append(step)

            history += f"\nAction: {parsed['name']}"
            history += f"\nAction Input: {parsed['input']}"
            history += f"\nObservation: {observation}\n"
        else:
            step["type"] = "unknown"
            steps.append(step)
            history += f"\n{response}\n"

    return {"answer": "达到最大迭代次数", "steps": steps, "iterations": max_iterations}


print("\n=== 题目 5: 完整 Agent ===")
result = agent_run("帮我查一下 Python 最新版本，然后计算 3.12 * 100 是多少")
print(f"答案: {result['answer']}")
print(f"迭代: {result['iterations']} 次")
for s in result["steps"]:
    if s["type"] == "action":
        print(f"  [{s['iteration']}] {s['tool']}({s['input']}) → {str(s['observation'])[:60]}...")
    elif s["type"] == "final":
        print(f"  [{s['iteration']}] Final Answer")
