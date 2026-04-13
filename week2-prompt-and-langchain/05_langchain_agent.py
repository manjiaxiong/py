# ===========================================
# Day 5: LangChain Agent + Tool — 让 AI 自主行动
# ===========================================
# Day 4 你学了 Chain：prompt → model → parser，流程是固定的
# Agent 不一样 — AI 自己决定调什么工具、调几次、什么时候停
#
# 类比：
# Chain = 流水线工人，按固定步骤干活
# Agent = 项目经理，自己判断该做什么
#
# Day 2 你用原生 SDK 写过 Tool Use，Agent 就是 LangChain 版的 Tool Use
# 但更强大：支持多轮调用、自动循环、内置工具
# ===========================================

# 安装（Day 4 已装过 langchain，这里不需要额外安装）

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(
    model=os.getenv("MINIMAX_MODEL_NAME"),
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
    max_tokens=500,
)


# ===========================================
# 1. Agent 的核心概念
# ===========================================
# Agent 的工作循环（ReAct 模式）：
#
#   用户提问
#     ↓
#   AI 思考：我需要用什么工具？ ← Reasoning
#     ↓
#   AI 调用工具              ← Acting
#     ↓
#   拿到工具结果              ← Observation
#     ↓
#   AI 判断：够了吗？
#     ↓          ↓
#    不够        够了
#   (继续循环)   → 返回最终回答
#
# JS 类比：
# 就像一个 while 循环：
# while (!done) {
#   const action = ai.decide(question, toolResults)
#   const result = executeTool(action)
#   if (ai.isSatisfied(result)) done = true
# }
#
# 和 Day 2 原生 Tool Use 的区别：
# - 原生 Tool Use：你手动写循环，手动拼 messages
# - Agent：LangChain 帮你写好了循环逻辑

print("=== 1. Agent 核心概念 ===\n")
print("""
Chain vs Agent：

| 维度     | Chain              | Agent                    |
|----------|-------------------|--------------------------|
| 流程     | 固定的管道         | AI 自己决定              |
| 工具调用 | 不调 / 强制调一次  | 调 0 次或多次            |
| 循环     | 不循环             | 自动循环直到满意         |
| 适用场景 | 流程确定的任务     | 开放式、多步骤任务       |
""")


# ===========================================
# 2. 定义工具 — 用 @tool 装饰器
# ===========================================
# LangChain 用 @tool 装饰器把普通函数变成工具
# AI 根据函数名和 docstring 来决定什么时候调用
#
# 类比 Day 2 原生 Tool Use：
# 原生：手动写 JSON Schema（name, description, input_schema）
# LangChain：写个函数 + docstring，自动生成 Schema

print(f"\n{'='*50}")
print("=== 2. 定义工具 ===\n")


@tool
def get_weather(city: str) -> str:
    """查询城市天气。当用户问天气相关问题时使用。

    Args:
        city: 城市名称，如 北京、上海
    """
    # 模拟天气数据（实际项目调天气 API）
    weather_data = {
        "北京": "晴，25°C，湿度 40%",
        "上海": "多云，22°C，湿度 65%",
        "深圳": "阵雨，28°C，湿度 80%",
    }
    return weather_data.get(city, f"{city}：暂无天气数据")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。当用户需要数学计算时使用。

    Args:
        expression: 数学表达式，如 (100 + 200) * 0.8
    """
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@tool
def search_product(query: str, max_price: float = 99999) -> str:
    """搜索商品信息。当用户问商品、价格相关问题时使用。

    Args:
        query: 搜索关键词
        max_price: 最高价格限制
    """
    # 模拟商品数据
    products = [
        {"name": "iPhone 15", "price": 5999},
        {"name": "华为 Mate 60", "price": 6999},
        {"name": "小米 14", "price": 3999},
        {"name": "Redmi Note 13", "price": 1099},
    ]
    results = [p for p in products if query.lower() in p["name"].lower() or p["price"] <= max_price]
    if not results:
        return "没有找到相关商品"
    return str(results[:3])


# 看看工具的信息
# print(f"工具名: {get_weather.name}")
# print(f"工具描述: {get_weather.description}")
# print(f"参数 Schema: {get_weather.args_schema.model_json_schema()}")

# 对比 Day 2 原生写法：
# 原生 Tool Use 需要手动写这些：
# {
#     "name": "get_weather",
#     "description": "查询城市天气...",
#     "input_schema": {
#         "type": "object",
#         "properties": {
#             "city": {"type": "string", "description": "城市名称"}
#         },
#         "required": ["city"]
#     }
# }
# @tool 装饰器自动帮你生成了！


# ===========================================
# 3. 创建 Agent — 用 LangGraph 的 ReAct Agent
# ===========================================
# LangChain 推荐用 LangGraph 创建 Agent（更可控）
# create_react_agent 是最简单的方式

print(f"\n{'='*50}")
print("=== 3. 创建 Agent ===\n")

from langgraph.prebuilt import create_react_agent

# 把工具列表传给 Agent
tools = [get_weather, calculate, search_product]

agent = create_react_agent(
    model=llm,
    tools=tools,
)

# 调用 Agent
# result = agent.invoke({"messages": [HumanMessage(content="日本今天天气怎么样？")]})
# # # 打印最终回复（最后一条消息）
# print(f"回复: {result['messages'][-1].content}")


# ===========================================
# 4. 观察 Agent 执行过程
# ===========================================
# Agent 内部会经历多个步骤，我们可以用 stream 看到每一步
#
# JS 类比：
# 就像 Redux DevTools — 能看到每个 action 的派发过程

print(f"\n{'='*50}")
print("=== 4. 观察 Agent 执行过程 ===\n")


def run_agent_verbose(question):
    """运行 Agent 并打印每一步"""
    print(f"问题: {question}\n")

    for step in agent.stream({"messages": [HumanMessage(content=question)]}):
        # step 是一个 dict，key 是节点名
        for node_name, node_output in step.items():
            if node_name == "agent":
                # AI 的思考/工具调用决策
                msg = node_output["messages"][-1]
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"  [调用工具] {tc['name']}({tc['args']})")
                else:
                    print(f"  [最终回答] {msg.content}")
            elif node_name == "tools":
                # 工具执行结果
                msg = node_output["messages"][-1]
                print(f"  [工具结果] {msg.content}")

    print()


# 测试：简单问题（调一次工具）
run_agent_verbose("东京天气怎么样？")

# 测试：需要计算的问题
# run_agent_verbose("帮我算一下 (100 + 200) * 0.8 等于多少")

# 测试：不需要工具的问题（AI 直接回答）
# run_agent_verbose("你好，介绍一下你自己")


# ===========================================
# 5. 多工具协作 — Agent 自动选择和组合
# ===========================================
# Agent 最强的地方：面对复杂问题，自动拆分成多个步骤，调不同工具

print(f"\n{'='*50}")
print("=== 5. 多工具协作 ===\n")

# 测试：需要多个工具的复杂问题
# run_agent_verbose("北京今天天气怎么样？另外帮我算一下 365 * 24 是多少小时")

# 测试：带条件的搜索
# run_agent_verbose("有什么 5000 元以下的手机推荐吗？")


# ===========================================
# 6. 自定义更复杂的工具
# ===========================================
# 工具可以有多个参数、返回复杂结果

print(f"\n{'='*50}")
print("=== 6. 自定义复杂工具 ===\n")


@tool
def analyze_code(code: str, language: str = "Python") -> str:
    """分析代码质量并给出改进建议。当用户要求审查或分析代码时使用。

    Args:
        code: 要分析的代码
        language: 编程语言，默认 Python
    """
    # 简单的静态检查（实际项目可以用 AST 分析）
    issues = []
    if "eval(" in code:
        issues.append("安全风险：使用了 eval()，可能导致代码注入")
    if "except:" in code or "except Exception:" in code:
        issues.append("代码质量：异常捕获太宽泛，应该捕获具体异常")
    if len(code.split("\n")) > 50:
        issues.append("可维护性：函数过长，建议拆分")
    if "password" in code.lower() or "secret" in code.lower():
        issues.append("安全风险：代码中可能包含敏感信息")

    if not issues:
        return f"{language} 代码看起来不错，没有发现明显问题"
    return f"发现 {len(issues)} 个问题：\n" + "\n".join(f"- {i}" for i in issues)


# 创建带代码分析工具的 Agent
agent_with_code = create_react_agent(
    model=llm,
    tools=[get_weather, calculate, search_product, analyze_code],
)

# result = agent_with_code.invoke({
#     "messages": [HumanMessage(content="""帮我看看这段代码有什么问题：
# def login(user_input):
#     query = eval(f"SELECT * FROM users WHERE name = '{user_input}'")
#     return query
# """)]
# })
# print(f"回复: {result['messages'][-1].content}")


# ===========================================
# 7. Agent 的局限性和踩坑
# ===========================================

print(f"\n{'='*50}")
print("=== 7. Agent 的局限性 ===\n")

print("""
Agent 常见问题：

1. 死循环
   - AI 反复调同一个工具，停不下来
   - 解决：设置 max_iterations 限制最大循环次数

2. 选错工具
   - AI 误判应该调哪个工具
   - 解决：工具的 description 写清楚什么时候用

3. 参数填错
   - AI 给工具传了错误的参数
   - 解决：参数的 docstring 写清楚格式和示例

4. 幻觉
   - AI 不调工具，自己编造答案
   - 解决：在 system prompt 里要求"必须用工具查询"

5. 成本高
   - 每次循环都消耗 token（比 Chain 贵）
   - 解决：简单任务用 Chain，复杂任务才用 Agent

什么时候用 Agent vs Chain？

| 场景                    | 推荐       |
|------------------------|-----------|
| 固定流程（翻译、提取）  | Chain     |
| 需要判断用哪个工具      | Agent     |
| 多步骤、需要循环        | Agent     |
| 追求稳定和低成本        | Chain     |
| 开放式对话 + 工具       | Agent     |
""")


# ===========================================
# 8. 给 Agent 加系统提示
# ===========================================

print(f"\n{'='*50}")
print("=== 8. Agent + System Prompt ===\n")

agent_with_prompt = create_react_agent(
    model=llm,
    tools=tools,
    prompt="你是一个智能助手，能查天气、做计算、搜商品。用中文简洁回答。如果用户问的问题需要查询数据，必须使用工具，不要自己编造。",
)

# result = agent_with_prompt.invoke({
#     "messages": [HumanMessage(content="深圳天气怎么样？顺便帮我算下 99 * 12")]
# })
# print(f"回复: {result['messages'][-1].content}")


# ===========================================
# 总结
# ===========================================

print(f"\n{'='*50}")
print("=== 总结 ===")
print("""
LangChain Agent 核心：

1. @tool 装饰器    — 普通函数变工具，自动生成 Schema
2. create_react_agent — 创建 ReAct Agent（思考→行动→观察 循环）
3. agent.stream    — 观察 Agent 每一步的执行过程
4. 多工具协作      — Agent 自动选择和组合工具
5. System Prompt   — 约束 Agent 行为

vs Day 2 原生 Tool Use：
| 原生 Tool Use            | LangChain Agent           |
|--------------------------|---------------------------|
| 手动写 JSON Schema       | @tool 自动生成            |
| 手动写循环逻辑           | Agent 自动循环            |
| 手动拼 messages          | 框架自动管理              |
| 更灵活，更底层           | 更方便，更高层            |

下一课：Day 6-7 周项目 — AI 数据助手
""")
