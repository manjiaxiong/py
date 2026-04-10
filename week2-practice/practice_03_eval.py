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

eval_cases = [
    {
        "id": "resume_001",
        "input": "张三，5年前端开发经验，熟练掌握 React、TypeScript、Node.js，本科毕业于浙江大学",
        "expected": {"name": "张三", "experience_years": 5, "skills": ["React", "TypeScript", "Node.js"], "education": "本科"},
        "check_fields": ["name", "experience_years", "skills", "education"],
        "tags": ["正常"],
    },
    {
        "id": "resume_002",
        "input": "李四，应届毕业生，了解 Python 和 HTML，本科学历",
        "expected": {"name": "李四", "experience_years": 0, "skills": ["Python", "HTML"], "education": "本科"},
        "check_fields": ["name", "experience_years", "skills"],
        "tags": ["应届生", "边界"],
    },
    {
        "id": "resume_003",
        "input": "王五，10年全栈开发，精通 Java、Spring、MySQL、Redis、Docker、Kubernetes、Go、Python，硕士毕业于北京大学",
        "expected": {"name": "王五", "experience_years": 10, "skills": ["Java", "Spring", "MySQL", "Redis", "Docker"], "education": "硕士"},
        "check_fields": ["name", "experience_years", "skills", "education"],
        "tags": ["多技能", "资深"],
    },
    {
        "id": "resume_004",
        "input": "赵六，3年经验，会 Vue",
        "expected": {"name": "赵六", "experience_years": 3, "skills": ["Vue"]},
        "check_fields": ["name", "experience_years", "skills"],
        "tags": ["信息不全", "边界"],
    },
    {
        "id": "resume_005",
        "input": "陈七，博士学历，8年 AI 研究经验，擅长 PyTorch、TensorFlow、LangChain、大模型微调",
        "expected": {"name": "陈七", "experience_years": 8, "skills": ["PyTorch", "TensorFlow", "LangChain"], "education": "博士"},
        "check_fields": ["name", "experience_years", "skills", "education"],
        "tags": ["AI", "高学历"],
    },
]

# print("=== 题目 1: 评估集 ===")
# for case in eval_cases:
#     print(f"  {case['id']}: {case['input'][:30]}... tags={case['tags']}")


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


def ask_with_log(prompt, system=""):
    """带日志的 API 调用"""
    start = time.time()

    kwargs = {
        "model": MODEL,
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    elapsed = time.time() - start

    text = response.content[0].text.strip()

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": text,
        "elapsed_ms": round(elapsed * 1000),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    request_logs.append(log_entry)
    return text, log_entry


# print("\n=== 题目 2: 带日志的 API 调用 ===")
# text, log = ask_with_log("1+1等于几？直接回答数字")
# print(f"回复: {text}")
# print(f"耗时: {log['elapsed_ms']}ms, token: {log['input_tokens']}+{log['output_tokens']}")


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


def check_result(actual, expected, check_fields):
    """
    对比实际输出和期望输出

    返回: (passed, reason)
    """
    if actual is None:
        return False, "实际结果为 None（JSON 解析失败？）"

    errors = []
    for field in check_fields:
        if field not in expected:
            continue

        exp_val = expected[field]
        act_val = actual.get(field)

        if act_val is None:
            errors.append(f"缺少字段 '{field}'")
            continue

        # 数字精确匹配
        if isinstance(exp_val, (int, float)):
            if act_val != exp_val:
                errors.append(f"字段 '{field}': 期望 {exp_val}, 实际 {act_val}")

        # 列表元素匹配（期望的每个元素都在实际列表中）
        elif isinstance(exp_val, list):
            if not isinstance(act_val, list):
                errors.append(f"字段 '{field}': 期望列表, 实际 {type(act_val).__name__}")
            else:
                actual_lower = [str(s).lower() for s in act_val]
                for item in exp_val:
                    if str(item).lower() not in actual_lower:
                        errors.append(f"字段 '{field}': 缺少 '{item}'")

        # 字符串包含匹配
        elif isinstance(exp_val, str):
            if exp_val not in str(act_val):
                errors.append(f"字段 '{field}': 期望包含 '{exp_val}', 实际 '{act_val}'")

    if errors:
        return False, "; ".join(errors)
    return True, "通过"


# print("\n=== 题目 3: 评估函数 ===")
# print(check_result({"name": "张三", "age": 25}, {"name": "张三", "age": 25}, ["name", "age"]))
# print(check_result({"name": "张三", "age": 24}, {"name": "张三", "age": 25}, ["name", "age"]))
# print(check_result(None, {"name": "张三"}, ["name"]))


# --- 提取函数（供评估使用）---

def clean_markdown(text):
    """清理 AI 回复中的 markdown 代码块"""
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()
    return raw


def extract_resume(text, system_override=None):
    """用 Prompt 约束法提取简历信息"""
    system = system_override or ""
    prompt = f"""从以下简历描述中提取信息，直接返回 JSON（不要加 markdown 代码块标记）：

格式：{{"name": "姓名", "experience_years": 数字, "skills": ["技能1", "技能2"], "education": "学历"}}

文本：{text}"""

    result, _ = ask_with_log(prompt, system=system)
    raw = clean_markdown(result)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# TODO 3.2: 实现 run_eval(cases)
# - 遍历 cases，对每条调用提取函数 + check_result
# - 统计: total, passed, failed, pass_rate, avg_latency_ms, total_tokens
# - 收集失败样本到 failures 列表
# - 打印每条 case 的 PASS/FAIL 状态
# - 返回 summary dict
# 测试（需要先完成题目 1 和 2）:
# summary = run_eval(eval_cases)
# print(f"通过率: {summary['pass_rate']}%")


def run_eval(cases, extract_fn=None):
    """
    运行评估

    参数:
        cases: 评估用例列表
        extract_fn: 提取函数，默认用 extract_resume

    返回:
        summary dict
    """
    if extract_fn is None:
        extract_fn = extract_resume

    total = len(cases)
    passed = 0
    failures = []
    total_latency = 0
    total_tokens = 0

    print(f"运行评估 — 共 {total} 条用例")
    print("-" * 50)

    for case in cases:
        case_id = case["id"]
        print(f"  [{case_id}] ", end="")

        start_log_count = len(request_logs)
        result = extract_fn(case["input"])

        # 从日志中取耗时和 token
        new_logs = request_logs[start_log_count:]
        for log in new_logs:
            total_latency += log["elapsed_ms"]
            total_tokens += log["input_tokens"] + log["output_tokens"]

        ok, reason = check_result(result, case["expected"], case["check_fields"])

        if ok:
            print("PASS")
            passed += 1
        else:
            print(f"FAIL — {reason}")
            failures.append({
                "id": case_id,
                "input": case["input"],
                "expected": case["expected"],
                "actual": result,
                "reason": reason,
            })

    failed = total - passed
    pass_rate = round(passed / total * 100, 1) if total > 0 else 0

    print("-" * 50)
    print(f"结果: {passed}/{total} 通过 ({pass_rate}%)")

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "avg_latency_ms": round(total_latency / total) if total > 0 else 0,
        "total_tokens": total_tokens,
        "failures": failures,
    }


# print("\n=== 题目 3.2: 运行评估 ===")
# summary = run_eval(eval_cases)
# print(f"平均耗时: {summary['avg_latency_ms']}ms, 总 token: {summary['total_tokens']}")


# --- 题目 4: 回归测试 ---

# TODO 4.1: 写两个版本的简历提取函数
# - extract_v1(text): 基础 prompt，直接要求返回 JSON
# - extract_v2(text): 改进版，加 few-shot 示例
# 两个函数都返回 dict 或 None


def extract_v1(text):
    """基础版：直接要求返回 JSON"""
    prompt = f"""从以下简历描述中提取信息，直接返回 JSON：

格式：{{"name": "姓名", "experience_years": 数字, "skills": ["技能1"], "education": "学历"}}

文本：{text}"""

    result, _ = ask_with_log(prompt)
    raw = clean_markdown(result)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def extract_v2(text):
    """改进版：加 few-shot 示例"""
    prompt = f"""从简历描述中提取信息，返回 JSON。

示例 1:
输入: "王小明，3年 Java 开发，精通 Spring 和 MySQL，本科毕业于武汉大学"
输出: {{"name": "王小明", "experience_years": 3, "skills": ["Java", "Spring", "MySQL"], "education": "本科"}}

示例 2:
输入: "小红，应届毕业生，学过 Python 和 C++，硕士学历"
输出: {{"name": "小红", "experience_years": 0, "skills": ["Python", "C++"], "education": "硕士"}}

现在请提取:
输入: "{text}"
输出: """

    result, _ = ask_with_log(prompt)
    raw = clean_markdown(result)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# TODO 4.2: 实现 regression_test(cases, v1_fn, v2_fn)
# - 用同一批 cases 分别跑 v1 和 v2
# - 对比通过率
# - 找出退化的 case（v1 通过但 v2 没通过的）
# - 打印对比结果
# 测试:
# regression_test(eval_cases, extract_v1, extract_v2)


def regression_test(cases, v1_fn, v2_fn):
    """
    回归测试：对比两个版本的提取函数

    找出退化（regression）= v1 通过但 v2 没通过
    """
    print("=== 回归测试 ===\n")

    print("--- V1 ---")
    summary_v1 = run_eval(cases, extract_fn=v1_fn)

    print("\n--- V2 ---")
    summary_v2 = run_eval(cases, extract_fn=v2_fn)

    # 对比
    print(f"\n{'='*50}")
    print(f"V1 通过率: {summary_v1['pass_rate']}%")
    print(f"V2 通过率: {summary_v2['pass_rate']}%")

    # 找退化的 case
    v1_failed_ids = {f["id"] for f in summary_v1["failures"]}
    v2_failed_ids = {f["id"] for f in summary_v2["failures"]}

    regressions = v2_failed_ids - v1_failed_ids  # V2 新增的失败
    improvements = v1_failed_ids - v2_failed_ids  # V2 修复的失败

    if regressions:
        print(f"\n退化（V1 通过但 V2 失败）: {regressions}")
    if improvements:
        print(f"改进（V1 失败但 V2 通过）: {improvements}")
    if not regressions and not improvements:
        print("\n两个版本结果一致")


# print("\n=== 题目 4: 回归测试 ===")
# regression_test(eval_cases, extract_v1, extract_v2)


# --- 题目 5: 日志持久化 + 失败报告 ---

# TODO 5.1: 实现 save_logs(logs, filename="debug_log.jsonl")
# - 把日志列表写到 JSONL 文件（每行一条 JSON）
# - 用追加模式（"a"）


def save_logs(logs, filename="debug_log.jsonl"):
    """把日志写到 JSONL 文件"""
    log_path = Path(__file__).parent / filename
    with open(log_path, "a", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
    print(f"已保存 {len(logs)} 条日志到 {log_path}")


# TODO 5.2: 实现 analyze_failures(summary)
# - 接收 run_eval 的返回值
# - 打印每条失败样本的: id, 输入, 期望, 实际, 原因
# - 统计失败模式（JSON 解析失败 / 字段错误 / 缺少字段）
# 测试:
# summary = run_eval(eval_cases)
# analyze_failures(summary)
# save_logs(request_logs)


def analyze_failures(summary):
    """分析失败样本"""
    failures = summary.get("failures", [])
    if not failures:
        print("没有失败样本")
        return

    print(f"\n=== 失败分析 — 共 {len(failures)} 条 ===\n")

    # 失败模式统计
    patterns = {"JSON 解析失败": 0, "字段错误": 0, "缺少字段": 0}

    for f in failures:
        print(f"ID: {f['id']}")
        print(f"  输入: {f['input'][:50]}...")
        print(f"  期望: {f['expected']}")
        print(f"  实际: {f['actual']}")
        print(f"  原因: {f['reason']}")
        print()

        # 归类失败模式
        reason = f["reason"]
        if f["actual"] is None:
            patterns["JSON 解析失败"] += 1
        elif "缺少字段" in reason:
            patterns["缺少字段"] += 1
        else:
            patterns["字段错误"] += 1

    print("失败模式统计:")
    for pattern, count in patterns.items():
        if count > 0:
            print(f"  {pattern}: {count} 次")


# print("\n=== 题目 5: 日志持久化 + 失败报告 ===")
# summary = run_eval(eval_cases)
# analyze_failures(summary)
# save_logs(request_logs)
