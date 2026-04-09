# ===========================================
# 练习 5：LangChain Agent + Tool（对应 Day 5）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 05_langchain_agent.py
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# TODO 0: 初始化 ChatOpenAI（自己写）
# - 用 .env 里的环境变量创建 llm


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


# --- 题目 2: 创建 Agent ---

# TODO 2.1: 用 create_react_agent 创建 Agent
# - 把题目 1 的 3 个工具传进去
# - 测试以下问题：
# print(ask_agent("我的订单 12345 现在什么状态？"))
# print(ask_agent("100 美元等于多少人民币？"))
# print(ask_agent("37 摄氏度等于多少华氏度？"))


# --- 题目 3: 观察 Agent 执行过程 ---

# TODO 3.1: 用 agent.stream 实现 run_agent_verbose(question)
# - 打印每一步：工具调用、工具结果、最终回答
# - 测试一个需要多步的问题：
# run_agent_verbose("订单 67890 什么状态？另外 1000 日元等于多少人民币？")


# --- 题目 4: 给 Agent 加 System Prompt ---

# TODO 4.1: 创建一个带 system prompt 的客服 Agent
# - system prompt: 你是电商客服，只回答订单查询、汇率换算、单位换算问题
# - 对于超出范围的问题，礼貌拒绝
# 测试:
# print(ask_support("订单 11111 到了吗？"))
# print(ask_support("今天天气怎么样？"))  # 应该拒绝


# --- 题目 5: 自定义复杂工具 ---

# TODO 5.1: 定义一个 code_reviewer 工具
# - 参数: code(str), language(str)
# - 检查常见问题：eval 使用、宽泛异常捕获、硬编码密码、过长函数
# - 返回问题列表或"代码没问题"
#
# TODO 5.2: 创建一个编程助手 Agent
# - 工具：code_reviewer + calculate
# - 测试：
# print(ask_dev_agent("帮我检查这段代码：\ndef hack(): return eval(input())"))
# print(ask_dev_agent("128 * 256 等于多少？"))
