# ===========================================
# 练习 5：LangChain Agent + Tool（对应 Day 5）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 05_langchain_agent.py
# ===========================================

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# TODO 0: 初始化 ChatOpenAI（自己写）
# - 用 .env 里的环境变量创建 llm

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(
    model=os.getenv("MINIMAX_MODEL_NAME"),
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
    max_tokens=500,
)


# --- 题目 1: 用 @tool 定义工具 ---

# TODO 1.1: 定义 3 个工具（用 @tool 装饰器）
# 1. query_order(order_id: str) → 查询订单状态
#    - 模拟数据：{"12345": "已发货", "67890": "待付款", "11111": "已完成"}
# 2. get_exchange_rate(currency: str) → 查询汇率
#    - 模拟数据：{"USD": 7.25, "EUR": 7.85, "JPY": 0.048}
# 3. unit_convert(value: float, from_unit: str, to_unit: str) → 单位换算
#    - 支持：km↔m, kg↔g, celsius↔fahrenheit
#
# 注意：docstring 要写清楚什么时候用这个工具！
# 测试:
# print(query_order.invoke("12345"))
# print(get_exchange_rate.invoke("USD"))
# print(unit_convert.invoke({"value": 100, "from_unit": "km", "to_unit": "m"}))


@tool
def query_order(order_id: str) -> str:
    """查询订单状态。当用户询问订单信息、物流进度时使用。

    Args:
        order_id: 订单号
    """
    orders = {"12345": "已发货", "67890": "待付款", "11111": "已完成"}
    status = orders.get(order_id, "未找到该订单")
    return json.dumps({"order_id": order_id, "status": status}, ensure_ascii=False)


@tool
def get_exchange_rate(currency: str) -> str:
    """查询外币对人民币汇率。当用户询问汇率、换算外币时使用。

    Args:
        currency: 货币代码，如 USD、EUR、JPY
    """
    rates = {"USD": 7.25, "EUR": 7.85, "JPY": 0.048}
    rate = rates.get(currency.upper())
    if rate:
        return json.dumps({"currency": currency.upper(), "rate_to_cny": rate}, ensure_ascii=False)
    return json.dumps({"error": f"不支持的货币: {currency}"}, ensure_ascii=False)


@tool
def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """单位换算。当用户需要换算长度(km/m)、重量(kg/g)、温度(celsius/fahrenheit)时使用。

    Args:
        value: 数值
        from_unit: 原始单位
        to_unit: 目标单位
    """
    conversions = {
        ("km", "m"): lambda v: v * 1000,
        ("m", "km"): lambda v: v / 1000,
        ("kg", "g"): lambda v: v * 1000,
        ("g", "kg"): lambda v: v / 1000,
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return json.dumps({
            "value": value, "from": from_unit, "to": to_unit,
            "result": round(result, 2),
        }, ensure_ascii=False)
    return json.dumps({"error": f"不支持的转换: {from_unit} → {to_unit}"}, ensure_ascii=False)


# print("=== 题目 1: 工具测试 ===")
# print(query_order.invoke("12345"))
# print(get_exchange_rate.invoke("USD"))
# print(unit_convert.invoke({"value": 100, "from_unit": "km", "to_unit": "m"}))


# --- 题目 2: 创建 Agent ---

# TODO 2.1: 用 create_react_agent 创建 Agent
# - 把题目 1 的 3 个工具传进去
# - 测试以下问题：
# print(ask_agent("我的订单 12345 现在什么状态？"))
# print(ask_agent("100 美元等于多少人民币？"))
# print(ask_agent("37 摄氏度等于多少华氏度？"))

tools = [query_order, get_exchange_rate, unit_convert]

agent = create_react_agent(model=llm, tools=tools)


def ask_agent(question):
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


# print("\n=== 题目 2: Agent 测试 ===")
# print(ask_agent("我的订单 12345 现在什么状态？"))
# print(ask_agent("100 美元等于多少人民币？"))
# print(ask_agent("37 摄氏度等于多少华氏度？"))


# --- 题目 3: 观察 Agent 执行过程 ---

# TODO 3.1: 用 agent.stream 实现 run_agent_verbose(question)
# - 打印每一步：工具调用、工具结果、最终回答
# - 测试一个需要多步的问题：
# run_agent_verbose("订单 67890 什么状态？另外 1000 日元等于多少人民币？")


def run_agent_verbose(question):
    print(f"问题: {question}\n")

    for step in agent.stream({"messages": [HumanMessage(content=question)]}):
        for node_name, node_output in step.items():
            if node_name == "agent":
                msg = node_output["messages"][-1]
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"  [调用工具] {tc['name']}({tc['args']})")
                else:
                    print(f"  [最终回答] {msg.content[:200]}")
            elif node_name == "tools":
                msg = node_output["messages"][-1]
                content = msg.content if len(msg.content) <= 100 else msg.content[:100] + "..."
                print(f"  [工具结果] {content}")

    print()


# print("\n=== 题目 3: 观察执行过程 ===")
# run_agent_verbose("订单 67890 什么状态？另外 1000 日元等于多少人民币？")


# --- 题目 4: 给 Agent 加 System Prompt ---

# TODO 4.1: 创建一个带 system prompt 的客服 Agent
# - system prompt: 你是电商客服，只回答订单查询、汇率换算、单位换算问题
# - 对于超出范围的问题，礼貌拒绝
# 测试:
# print(ask_support("订单 11111 到了吗？"))
# print(ask_support("今天天气怎么样？"))  # 应该拒绝

SUPPORT_PROMPT = """你是一个电商客服助手，只能处理以下类型的问题：
1. 订单查询 — 查订单状态
2. 汇率换算 — 查外币汇率
3. 单位换算 — km/m、kg/g、温度换算

对于超出以上范围的问题，礼貌地告知用户你只能处理这三类问题。
用中文回答，简洁友好。"""

support_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SUPPORT_PROMPT,
)


def ask_support(question):
    result = support_agent.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


# print("\n=== 题目 4: 客服 Agent ===")
# print(ask_support("订单 11111 到了吗？"))
# print(ask_support("今天天气怎么样？"))


# --- 题目 5: 自定义复杂工具 ---

# TODO 5.1: 定义一个 code_reviewer 工具
# - 参数: code(str), language(str)
# - 检查常见问题：eval 使用、宽泛异常捕获、硬编码密码、过长函数
# - 返回问题列表或"代码没问题"


@tool
def code_reviewer(code: str, language: str) -> str:
    """检查代码中的常见问题。当用户要求审查代码时使用。

    Args:
        code: 要审查的代码
        language: 编程语言，如 python, javascript
    """
    issues = []

    # 检查 eval 使用
    if "eval(" in code:
        issues.append("危险：使用了 eval()，可能导致代码注入攻击")

    # 检查宽泛异常捕获
    if "except:" in code or "except Exception:" in code:
        issues.append("警告：过于宽泛的异常捕获，建议捕获具体异常类型")

    # 检查硬编码密码
    for keyword in ["password", "secret", "api_key", "token"]:
        if f'{keyword} = "' in code.lower() or f"{keyword} = '" in code.lower():
            issues.append(f"严重：疑似硬编码了 {keyword}，应使用环境变量")

    # 检查函数长度（简单统计行数）
    lines = [l for l in code.strip().split("\n") if l.strip()]
    if len(lines) > 30:
        issues.append(f"建议：函数过长（{len(lines)} 行），考虑拆分")

    if not issues:
        return json.dumps({"status": "通过", "message": "代码没有发现明显问题"}, ensure_ascii=False)

    return json.dumps({
        "status": "有问题",
        "issues": issues,
        "count": len(issues),
    }, ensure_ascii=False)


@tool
def calculate(expression: str) -> str:
    """数学计算器。当用户需要计算数学表达式时使用。

    Args:
        expression: 数学表达式，如 128 * 256
    """
    try:
        result = eval(expression)
        return json.dumps({"expression": expression, "result": result}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# TODO 5.2: 创建一个编程助手 Agent
# - 工具：code_reviewer + calculate
# - 测试：
# print(ask_dev_agent("帮我检查这段代码：\ndef hack(): return eval(input())"))
# print(ask_dev_agent("128 * 256 等于多少？"))

DEV_PROMPT = """你是一个编程助手，能帮用户：
1. 审查代码 — 检查安全漏洞、代码规范问题
2. 数学计算 — 计算数学表达式

用中文回答，给出专业建议。"""

dev_agent = create_react_agent(
    model=llm,
    tools=[code_reviewer, calculate],
    prompt=DEV_PROMPT,
)


def ask_dev_agent(question):
    result = dev_agent.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content


# print("\n=== 题目 5: 编程助手 Agent ===")
# print(ask_dev_agent("帮我检查这段代码：\ndef hack(): return eval(input())"))
# print(ask_dev_agent("128 * 256 等于多少？"))
