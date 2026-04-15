# ===========================================
# Day 1: Agent 深入 — 从手写循环到 ReAct 模式
# ===========================================
# Agent = 让 AI 自主决策调用工具的循环
#
# 类比：
# Chain  = 流水线，固定步骤 A → B → C
# Agent  = 自主员工，看情况决定下一步做什么
#
# 前端类比：
# Chain  = Promise.then().then()  固定顺序
# Agent  = while(!done) { switch(action) { ... } }  动态决策
# ===========================================

# 安装（如果还没装）：
# pip install anthropic python-dotenv

import sys
import re
import math
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

client, MODEL = get_client(Path(__file__).parent / ".env")


# ===========================================
# 1. Agent vs Chain — 自主决策 vs 固定流程
# ===========================================

# Chain（固定流程）：步骤写死，不会变
# JS 类比：
# const result = await step1()
#   .then(step2)
#   .then(step3);

def chain_example(question):
    """
    固定流程示例：翻译 → 摘要 → 格式化

    不管输入什么，都走这三步
    """
    # Step 1: 翻译
    translated = ask(client, MODEL, f"把以下内容翻译成英文：{question}", max_tokens=300)
    # Step 2: 摘要
    summary = ask(client, MODEL, f"用一句话总结：{translated}", max_tokens=100)
    # Step 3: 格式化
    result = f"📝 原文：{question}\n🌐 翻译：{translated}\n📌 摘要：{summary}"
    return result


# Agent（自主决策）：根据情况决定下一步
# JS 类比：
# while (!done && attempts < max) {
#   const action = await llm.decide(context);
#   const result = await tools[action.name](action.input);
#   context.push(result);
# }

print("=== Section 1: Agent vs Chain ===")
print("Chain = 固定流程 A → B → C")
print("Agent = 看情况决定下一步（循环 + 判断）")
print()

# Chain 示例
# result = chain_example("Python 是一种编程语言")
# print(result)


# ===========================================
# 2. ReAct 模式实战
# ===========================================
# ReAct = Reasoning（推理）+ Acting（行动）
#
# 流程：
# Thought → 分析当前状况
# Action → 选择工具
# Observation → 看到工具返回结果
# ... 循环 ...
# Final Answer → 输出最终答案
#
# JS 类比：
# async function reactLoop(task) {
#   while (true) {
#     const { thought, action } = await llm.reason(history);
#     if (action === 'final_answer') return thought;
#     const observation = await tools[action.name](action.input);
#     history.push({ thought, action, observation });
#   }
# }
# ===========================================

# 定义 3 个模拟工具
def calculator(expression):
    """
    计算数学表达式

    JS 类比：eval(expr)，但更安全
    """
    try:
        # 只允许安全的数学运算
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expression):
            return str(eval(expression))
        return f"不支持的表达式: {expression}"
    except Exception as e:
        return f"计算错误: {e}"


def search(query):
    """
    模拟搜索工具（实际项目中接真实 API）

    JS 类比：fetch('/api/search?q=' + query)
    """
    # 模拟搜索结果
    mock_results = {
        "python": "Python 3.12 是最新稳定版，发布于 2024 年。主要新特性包括更好的错误提示和性能优化。",
        "fastapi": "FastAPI 是高性能 Python Web 框架，基于 Starlette 和 Pydantic，支持异步。",
        "react": "React 18 支持并发特性、自动批处理、Suspense 改进。",
        "langgraph": "LangGraph 是 LangChain 团队开发的 Agent 编排框架，基于图结构。",
    }
    query_lower = query.lower()
    for key, value in mock_results.items():
        if key in query_lower:
            return value
    return f"关于 '{query}' 的搜索结果：暂无相关信息。"


def get_current_time(format_str=""):
    """获取当前时间"""
    now = datetime.now()
    if format_str:
        return now.strftime(format_str)
    return now.strftime("%Y-%m-%d %H:%M:%S")


# 工具注册表 — 就像一个 dict 版的路由表
# JS 类比：const tools = { calculator: fn, search: fn }
TOOLS = {
    "calculator": {
        "fn": calculator,
        "description": "计算数学表达式，如 2+3、100/4、(5+3)*2",
    },
    "search": {
        "fn": search,
        "description": "搜索信息，输入搜索关键词",
    },
    "get_current_time": {
        "fn": get_current_time,
        "description": "获取当前时间，可选格式如 %Y-%m-%d",
    },
}

# 构造工具描述（给 AI 看）
TOOL_DESCRIPTIONS = "\n".join(
    f"- {name}: {info['description']}" for name, info in TOOLS.items()
)

# ReAct Prompt 模板
REACT_PROMPT = """你是一个推理助手。你可以使用以下工具：

{tools}

请严格按照以下格式回答（每次只能选一个工具）：

Thought: 分析当前情况
Action: 工具名（从上面的工具中选）
Action Input: 工具的输入参数

当你得到足够信息可以给出最终答案时，输出：

Thought: 我已经有足够的信息了
Final Answer: 你的最终答案

注意：
- 每次只输出一个 Thought + Action 或 Thought + Final Answer
- 不要编造工具不存在的信息

用户任务：{task}

{history}"""


def parse_react_response(response):
    """
    从 LLM 输出中解析 Action 和 Input

    返回:
        {"type": "action", "name": "...", "input": "..."} 或
        {"type": "final", "answer": "..."}
    """
    # 检查是否有 Final Answer
    final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
    if final_match:
        return {"type": "final", "answer": final_match.group(1).strip()}

    # 解析 Action 和 Action Input
    action_match = re.search(r"Action:\s*(.+)", response)
    input_match = re.search(r"Action Input:\s*(.+)", response)

    if action_match:
        return {
            "type": "action",
            "name": action_match.group(1).strip(),
            "input": input_match.group(1).strip() if input_match else "",
        }

    return {"type": "unknown", "raw": response}


# 运行一次 ReAct 循环
# print("\n=== Section 2: ReAct 模式 ===")
# task = "Python 最新版本是什么？计算 3.12 * 100 等于多少？"
# history = ""
# max_iterations = 5
#
# for i in range(max_iterations):
#     prompt = REACT_PROMPT.format(tools=TOOL_DESCRIPTIONS, task=task, history=history)
#     response = ask(client, MODEL, prompt, max_tokens=500)
#     print(f"\n--- 第 {i+1} 轮 ---")
#     print(response)
#
#     parsed = parse_react_response(response)
#
#     if parsed["type"] == "final":
#         print(f"\n✅ 最终答案: {parsed['answer']}")
#         break
#     elif parsed["type"] == "action":
#         tool_name = parsed["name"]
#         tool_input = parsed["input"]
#         if tool_name in TOOLS:
#             observation = TOOLS[tool_name]["fn"](tool_input)
#         else:
#             observation = f"工具 {tool_name} 不存在"
#         print(f"  🔧 调用工具: {tool_name}({tool_input})")
#         print(f"  📋 Observation: {observation}")
#         history += f"\nThought: {response.split('Thought:')[-1].split('Action:')[0].strip() if 'Thought:' in response else ''}"
#         history += f"\nAction: {tool_name}"
#         history += f"\nAction Input: {tool_input}"
#         history += f"\nObservation: {observation}\n"
#     else:
#         print("  ⚠️ 无法解析 LLM 输出")
#         break
# else:
#     print("  ⚠️ 达到最大迭代次数")


# ===========================================
# 3. 为什么不是所有任务都适合 Agent
# ===========================================
# 适合 Agent：
# - 多步骤任务（需要查信息 → 计算 → 整合）
# - 不确定需要哪些步骤（让 AI 自己判断）
# - 需要调用外部工具
#
# 不适合 Agent：
# - 简单翻译/摘要（一次调用就够）
# - 固定格式输出（Chain 更稳定）
# - 对延迟敏感的场景（Agent 多轮调用很慢）
#
# JS 类比：不是所有逻辑都需要 while(true)
# 很多场景 if/else 就够了，循环反而更慢更不可控

# print("\n=== Section 3: Agent 适用场景 ===")
# print("┌──────────────────┬──────────────────────┐")
# print("│    适合 Agent     │    不适合 Agent       │")
# print("├──────────────────┼──────────────────────┤")
# print("│ 多步骤研究任务    │ 简单翻译/摘要         │")
# print("│ 需要多个工具配合  │ 固定格式输出          │")
# print("│ 路径不确定       │ 对延迟敏感的场景       │")
# print("│ 探索性问题       │ 一次调用就能完成       │")
# print("└──────────────────┴──────────────────────┘")
#
# # 对比：同一个任务用 Agent 和直接调用
# simple_task = "把 Hello World 翻译成中文"
#
# # 直接调用（推荐）
# direct_result = ask(client, MODEL, f"翻译成中文：Hello World", max_tokens=50)
# print(f"\n直接调用: {direct_result}")  # 快，一步到位
#
# # 用 Agent 就大材小用了 — 多轮调用，更慢，没有额外价值


# ===========================================
# 4. 停止条件与失败回退
# ===========================================
# Agent 必须有明确的停止条件，否则会无限循环！
#
# 停止条件：
# 1. LLM 输出了 Final Answer → 正常结束
# 2. 达到 max_iterations → 强制结束
# 3. 工具调用失败且重试耗尽 → 报错结束
#
# JS 类比：
# while (attempts < MAX && !result) {
#   try { result = await doWork(); }
#   catch(e) { attempts++; if (attempts >= MAX) throw e; }
# }

class SimpleAgent:
    """
    最小 Agent 实现

    JS 类比：
    class Agent {
        constructor(tools, maxIterations = 5) { ... }
        async run(task) { while(!done && i < max) { ... } }
    }
    """

    def __init__(self, client, model, tools, max_iterations=5, max_retries=2):
        """
        参数:
            client: AI 客户端
            model: 模型名称
            tools: 工具注册表 {name: {fn, description}}
            max_iterations: 最大迭代次数（防死循环）
            max_retries: 工具调用失败最大重试次数
        """
        self.client = client
        self.model = model
        self.tools = tools
        self.max_iterations = max_iterations
        self.max_retries = max_retries

        self.tool_descriptions = "\n".join(
            f"- {name}: {info['description']}" for name, info in tools.items()
        )

    def _execute_tool(self, tool_name, tool_input):
        """
        调用工具，带重试机制

        JS 类比：
        async function callWithRetry(fn, input, maxRetries) {
            for (let i = 0; i < maxRetries; i++) {
                try { return await fn(input); }
                catch(e) { if (i === maxRetries - 1) throw e; }
            }
        }
        """
        if tool_name not in self.tools:
            return f"❌ 工具 '{tool_name}' 不存在，可用工具: {list(self.tools.keys())}"

        for attempt in range(self.max_retries):
            try:
                result = self.tools[tool_name]["fn"](tool_input)
                return result
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"  ⚠️ 工具 {tool_name} 执行失败（第 {attempt+1} 次），重试...")
                else:
                    return f"❌ 工具 {tool_name} 执行失败: {e}"

    def run(self, task):
        """
        执行 Agent 循环

        返回:
            {"answer": 最终回答, "steps": 执行步骤列表, "iterations": 迭代次数}
        """
        history = ""
        steps = []

        for i in range(self.max_iterations):
            # 构造 prompt
            prompt = REACT_PROMPT.format(
                tools=self.tool_descriptions,
                task=task,
                history=history,
            )

            # 调 LLM
            response = ask(self.client, self.model, prompt, max_tokens=500)
            parsed = parse_react_response(response)

            step = {"iteration": i + 1, "raw_response": response}

            if parsed["type"] == "final":
                step["type"] = "final_answer"
                step["answer"] = parsed["answer"]
                steps.append(step)
                return {
                    "answer": parsed["answer"],
                    "steps": steps,
                    "iterations": i + 1,
                }

            elif parsed["type"] == "action":
                tool_name = parsed["name"]
                tool_input = parsed["input"]

                # 执行工具
                observation = self._execute_tool(tool_name, tool_input)

                step["type"] = "tool_call"
                step["tool"] = tool_name
                step["input"] = tool_input
                step["observation"] = observation
                steps.append(step)

                # 更新 history
                history += f"\nAction: {tool_name}"
                history += f"\nAction Input: {tool_input}"
                history += f"\nObservation: {observation}\n"

            else:
                step["type"] = "parse_error"
                steps.append(step)
                history += f"\n{response}\n"

        # 达到最大迭代次数
        return {
            "answer": "⚠️ 达到最大迭代次数，未能得出最终答案",
            "steps": steps,
            "iterations": self.max_iterations,
        }


# print("\n=== Section 4: SimpleAgent 类 ===")
# agent = SimpleAgent(client, MODEL, TOOLS, max_iterations=5)
# result = agent.run("现在几点了？然后计算 24 - 当前的小时数，告诉我今天还剩多少小时")
# print(f"\n最终答案: {result['answer']}")
# print(f"迭代次数: {result['iterations']}")
# for step in result["steps"]:
#     if step["type"] == "tool_call":
#         print(f"  🔧 [{step['iteration']}] {step['tool']}({step['input']}) → {step['observation']}")


# ===========================================
# 5. 完整多步骤任务演示
# ===========================================
# 任务：帮我查一下 FastAPI 是什么，再查一下 React 最新版本，
# 然后计算如果一个项目前端用 React 后端用 FastAPI 需要学多少天
# （假设每个技术学 5 天）

print("\n=== Section 5: 完整多步骤任务 ===")
agent = SimpleAgent(client, MODEL, TOOLS, max_iterations=6)
task = "帮我查一下 FastAPI 是什么，再查一下 React 最新版本，然后计算两个技术各学 5 天一共需要多少天"

print(f"任务: {task}\n")
result = agent.run(task)

print(f"\n{'='*50}")
print(f"✅ 最终答案: {result['answer']}")
print(f"📊 总迭代: {result['iterations']} 次")
print(f"\n执行过程:")
for step in result["steps"]:
    if step["type"] == "tool_call":
        print(f"  [{step['iteration']}] 🔧 {step['tool']}({step['input']})")
        print(f"       → {step['observation'][:80]}...")
    elif step["type"] == "final_answer":
        print(f"  [{step['iteration']}] ✅ Final Answer")
