# ===========================================
# 练习 3：评估与调试（对应 Day 3）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 03_eval_and_debug.py
# ===========================================

import os
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

# TODO 0: 初始化（自己写）
load_dotenv(Path(__file__).parent / ".env")

client = Anthropic(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url=os.getenv("MINIMAX_API_BASE"),
)
MODEL = os.getenv("MINIMAX_MODEL_NAME")


# --- 题目 1: 构建评估集 ---

# TODO 1.1: 给简历提取器写一个评估集
# - 至少 5 条 test case
# - 每条包含: id, input, expected, check_fields, tags
# - 覆盖：正常 case、边界 case（应届生/信息不全/多技能）
# - 直接写成 Python list（不用读 JSON 文件）

# eval_cases = [
#     {
#         "id": "resume_001",
#         "input": "...",
#         "expected": {"name": "...", "experience_years": ..., "skills": [...], "education": "..."},
#         "check_fields": ["name", "experience_years"],
#         "tags": ["简历提取"],
#     },
#     # ... 再写 4 条
# ]


# --- 题目 2: 带日志的 API 调用 ---

# TODO 2.1: 实现 ask_with_log(prompt, system="")
# - 调用 API 并记录日志
# - 日志包含: timestamp, prompt, response, elapsed_ms, input_tokens, output_tokens
# - 把日志存到一个全局列表 request_logs 中
# - 返回 (response_text, log_entry)
# 测试:
# text, log = ask_with_log("1+1等于几？直接回答数字")
# print(f"回复: {text}")
# print(f"耗时: {log['elapsed_ms']}ms, token: {log['input_tokens']}+{log['output_tokens']}")

request_logs = []


# --- 题目 3: 评估函数 ---

# TODO 3.1: 实现 check_result(actual, expected, check_fields)
# - 对比实际输出和期望输出
# - 支持三种匹配：
#   1. 数字精确匹配
#   2. 字符串包含匹配
#   3. 列表元素匹配（期望的每个元素都在实际列表中）
# - 返回 (passed: bool, reason: str)
# 测试:
# print(check_result({"name": "张三", "age": 25}, {"name": "张三", "age": 25}, ["name", "age"]))
# print(check_result({"name": "张三", "age": 24}, {"name": "张三", "age": 25}, ["name", "age"]))
# print(check_result(None, {"name": "张三"}, ["name"]))


# TODO 3.2: 实现 run_eval(cases)
# - 遍历 cases，对每条调用提取函数 + check_result
# - 统计: total, passed, failed, pass_rate, avg_latency_ms, total_tokens
# - 收集失败样本到 failures 列表
# - 打印每条 case 的 PASS/FAIL 状态
# - 返回 summary dict
# 测试（需要先完成题目 1 和 2）:
# summary = run_eval(eval_cases)
# print(f"通过率: {summary['pass_rate']}%")


# --- 题目 4: 回归测试 ---

# TODO 4.1: 写两个版本的简历提取函数
# - extract_v1(text): 基础 prompt，直接要求返回 JSON
# - extract_v2(text): 改进版，加 few-shot 示例
# 两个函数都返回 dict 或 None

# TODO 4.2: 实现 regression_test(cases, v1_fn, v2_fn)
# - 用同一批 cases 分别跑 v1 和 v2
# - 对比通过率
# - 找出退化的 case（v1 通过但 v2 没通过的）
# - 打印对比结果
# 测试:
# regression_test(eval_cases, extract_v1, extract_v2)


# --- 题目 5: 日志持久化 + 失败报告 ---

# TODO 5.1: 实现 save_logs(logs, filename="debug_log.jsonl")
# - 把日志列表写到 JSONL 文件（每行一条 JSON）
# - 用追加模式（"a"）

# TODO 5.2: 实现 analyze_failures(summary)
# - 接收 run_eval 的返回值
# - 打印每条失败样本的: id, 输入, 期望, 实际, 原因
# - 统计失败模式（JSON 解析失败 / 字段错误 / 缺少字段）
# 测试:
# summary = run_eval(eval_cases)
# analyze_failures(summary)
# save_logs(request_logs)
