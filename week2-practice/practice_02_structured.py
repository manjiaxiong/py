# ===========================================
# 练习 2：结构化输出（对应 Day 2）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 02_structured_output.py
# ===========================================

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# TODO 0: 初始化（自己写）
load_dotenv(Path(__file__).parent / ".env")


# --- 题目 1: Prompt 约束法提取 ---

# TODO 1.1: 写一个函数 extract_resume(text)
# - 用 Prompt 约束法从简历描述中提取信息
# - 返回 JSON: {"name": "", "experience_years": 数字, "skills": [], "education": ""}
# - 要处理 JSON 解析失败的情况
# 测试:
# print(extract_resume("张三，5年前端开发经验，熟练掌握 React、TypeScript、Node.js，本科毕业于浙江大学"))
# print(extract_resume("李四，3年 Python 后端开发，精通 Django 和 FastAPI，硕士毕业于清华大学"))


# --- 题目 2: Tool Use 单工具 ---

# TODO 2.1: 定义一个 extract_restaurant 工具
# - 从餐厅评价中提取: name, rating(1-5), cuisine(菜系), price_per_person(人均), recommendation(推荐菜)
# - rating 和 price_per_person 是 number 类型
# - recommendation 是 array 类型（字符串数组）
# 测试:
# print(extract_restaurant("昨天去了海底捞，环境不错服务很好，川菜火锅，人均150，推荐番茄锅底和虾滑"))
# print(extract_restaurant("外婆家的西湖醋鱼真不错，杭帮菜，人均80，4星推荐，还有东坡肉也好吃"))


# --- 题目 3: 多工具路由 ---

# TODO 3.1: 实现一个智能客服路由器 smart_support(user_input)
# - 定义 3 个工具:
#   1. check_order: 查订单（参数: order_id）
#   2. report_issue: 报告问题（参数: issue_type, description）
#   3. request_refund: 申请退款（参数: order_id, reason）
# - AI 根据用户输入自动选择合适的工具
# - 返回 {"tool": "工具名", "params": {...}}
# 测试:
# print(smart_support("我的订单 #12345 到哪了"))
# print(smart_support("收到的商品有破损，屏幕裂了"))
# print(smart_support("订单 #67890 我要退款，发错颜色了"))


# --- 题目 4: 完整 Tool Use 流程 ---

# TODO 4.1: 实现一个带工具执行的完整对话 chat_with_tools(user_input)
# - 定义一个 calculate 工具（参数: expression）
# - 定义一个 translate 工具（参数: text, target_lang）
# - 完整流程: 用户提问 → AI 选工具 → 执行工具 → 返回结果 → AI 生成最终回复
# - 模拟执行工具（calculate 用 eval，translate 返回模拟结果）
# 测试:
# print(chat_with_tools("帮我算一下 (100 + 200) * 0.8 是多少"))
# print(chat_with_tools("把 'Hello World' 翻译成日语"))


# --- 题目 5: Pydantic 验证 ---

# TODO 5.1: 用 Pydantic 定义一个 MovieReview 模型
# - title: str（必填）
# - rating: float（1-10 之间）
# - genre: str（类型，如 "科幻"、"喜剧"）
# - summary: str（一句话总结，最多 100 字）
# - recommend: bool（是否推荐）
#
# 写一个函数 extract_movie_review(text)：
# 1. 用 Tool Use 提取数据
# 2. 用 Pydantic 验证
# 3. 返回验证后的 MovieReview 对象
# 测试:
# print(extract_movie_review("看了《星际穿越》，科幻神作，打9分，诺兰的时空叙事太震撼了，强烈推荐"))
# print(extract_movie_review("《熊出没》还行吧，动画片，给6分，适合小朋友看，大人就算了"))
