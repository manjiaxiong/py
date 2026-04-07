# ===========================================
# 练习 1：Prompt Engineering（对应 Day 1）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 01_prompt_engineering.py
# ===========================================

import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# TODO 0: 初始化（自己写，别复制）
# - 加载 .env
# - 创建 client
# - 定义 MODEL

load_dotenv(Path(__file__).parent / ".env")


# --- 题目 1: Few-shot 数据提取器 ---

# TODO 1.1: 写一个函数 extract_product(text)
# - 用 Few-shot prompting 从商品描述中提取结构化信息
# - 输入: "iPhone 15 Pro Max 256GB 钛金属色 官方价 9999 元"
# - 输出: {"name": "iPhone 15 Pro Max", "storage": "256GB", "color": "钛金属色", "price": 9999}
# - 至少给 2 个 few-shot 示例
# 测试:
# print(extract_product("MacBook Air M3 16GB+512GB 星光色 售价 10499 元"))
# print(extract_product("华为 Mate 60 Pro 512GB 雅丹黑 售价 6999 元"))


# --- 题目 2: Chain-of-Thought 代码分析 ---

# TODO 2.1: 写一个函数 analyze_complexity(code)
# - 让 AI 分步分析代码的时间复杂度和空间复杂度
# - 要求 AI 展示推理过程，不是直接给结论
# - System Prompt 要求 AI 按步骤回答
# 测试:
# analyze_complexity("""
# def two_sum(nums, target):
#     seen = {}
#     for i, num in enumerate(nums):
#         complement = target - num
#         if complement in seen:
#             return [seen[complement], i]
#         seen[num] = i
#     return []
# """)


# --- 题目 3: System Prompt 角色扮演 ---

# TODO 3.1: 写一个函数 multi_role_review(code)
# - 让 3 个不同角色审查同一段代码:
#   1. 安全专家（关注安全漏洞）
#   2. 性能专家（关注性能瓶颈）
#   3. 可读性专家（关注代码风格和命名）
# - 每个角色用不同的 System Prompt
# - 打印每个角色的审查意见
# 测试:
# multi_role_review("""
# def get_user_data(user_id):
#     query = f"SELECT * FROM users WHERE id = {user_id}"
#     result = db.execute(query)
#     data = []
#     for row in result:
#         data.append({"id": row[0], "name": row[1], "email": row[2]})
#     return data
# """)


# --- 题目 4: Prompt 模板引擎 ---

# TODO 4.1: 写一个 PromptTemplate 类
# - __init__(self, template): 接收模板字符串
# - render(**kwargs): 填充变量，返回完整 prompt
# - 支持默认值（如果变量没传，用默认值）
# 测试:
# tpl = PromptTemplate("把以下 {source_lang} 代码翻译成 {target_lang}:\n{code}")
# prompt = tpl.render(source_lang="JavaScript", target_lang="Python", code="const x = 1")
# print(prompt)

# TODO 4.2: 用你的 PromptTemplate 类做一个 "错误诊断器"
# - 模板包含: 错误信息、代码、语言
# - 让 AI 诊断错误原因并给出修复代码
# 测试:
# error_tpl = PromptTemplate(...)
# prompt = error_tpl.render(
#     language="Python",
#     error="TypeError: 'NoneType' object is not subscriptable",
#     code="result = get_user()['name']"
# )
# print(ask(prompt))


# --- 题目 5: 综合挑战 — Prompt 优化器 ---

# TODO 5.1: 写一个函数 optimize_prompt(original_prompt)
# - 把用户写的"懒 Prompt"用 AI 优化成结构化的好 Prompt
# - System Prompt: 你是 Prompt 优化专家，把模糊的提示词变成结构清晰的
# - 优化后的 Prompt 要包含：角色、任务、格式要求、约束
# 测试:
# print(optimize_prompt("帮我写个爬虫"))
# print(optimize_prompt("优化我的代码"))
