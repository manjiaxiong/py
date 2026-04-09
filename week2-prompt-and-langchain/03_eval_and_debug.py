# ===========================================
# Day 3: 评估与调试 — 让 AI 应用可测试、可观测
# ===========================================
# 传统软件：输入确定 → 输出确定 → 断言就行
# AI 应用：输入确定 → 输出不确定 → 怎么测？
#
# 这节课解决：
# 1. 怎么构建评估集（eval dataset）
# 2. 怎么自动跑评估
# 3. 怎么记录日志方便调试
# 4. 怎么做回归测试（改了 prompt 不退化）
# ===========================================

import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import get_client, clean_markdown

# 初始化
client, MODEL = get_client(Path(__file__).parent / ".env")


# ===========================================
# 1. 为什么 AI 应用需要评估
# ===========================================
# 传统单元测试：assert add(1, 2) == 3 → 永远成立
# AI 应用：assert extract("iPhone 15 8999元")["price"] == 8999 → 大概率成立，但偶尔不成立
#
# JS 类比：
# 传统测试 = Jest expect(fn()).toBe(value)
# AI 评估 = 更像 E2E 测试，跑一批 case，看通过率
#
# 关键区别：
# - 传统测试追求 100% 通过
# - AI 评估追求"通过率 >= 阈值"（比如 90%）
# - AI 评估还关心：延迟、成本、稳定性

print("=== 1. 评估的基本概念 ===\n")
print("""
传统软件测试 vs AI 应用评估：

| 维度     | 传统测试              | AI 评估                    |
|----------|----------------------|---------------------------|
| 输出     | 确定的                | 不确定的                   |
| 判断标准 | assert 精确匹配       | 关键字段匹配 / AI 评判     |
| 通过标准 | 100%                 | >= 阈值（如 90%）          |
| 关注指标 | 正确性               | 正确性 + 延迟 + 成本       |
| 何时跑   | 每次提交              | 改 prompt / 换模型时       |
""")


# ===========================================
# 2. 构建评估集 — 你的"测试用例库"
# ===========================================
# 评估集 = 一组 {输入, 期望输出} 的集合
# 存成 JSON 文件，方便管理和版本控制

# print(f"\n{'='*50}")
# print("=== 2. 构建评估集 ===\n")

# 加载评估集
eval_file = Path(__file__).parent / "eval_cases.json"
with open(eval_file, "r", encoding="utf-8") as f:
    eval_cases = json.load(f)

# print(f"加载了 {len(eval_cases)} 条评估用例")
# print(f"第一条: {json.dumps(eval_cases[0], ensure_ascii=False, indent=2)}")

# 评估集的设计原则：
# 1. 覆盖正常 case（基础输入）
# 2. 覆盖边界 case（信息不全、格式奇怪）
# 3. 每条都有 tags，方便按类别筛选
# 4. check_fields 指定哪些字段必须正确（不需要所有字段都精确匹配）


# ===========================================
# 3. 带日志的 API 调用 — 可观测性
# ===========================================
# 每次调 API 都要记录：prompt、response、耗时、token
# 出问题时才能快速定位
#
# JS 类比：
# 就像给 fetch 加 interceptor 记录请求日志
# axios.interceptors.request.use(config => { console.log(config); return config })

# print(f"\n{'='*50}")
# print("=== 3. 带日志的 API 调用 ===\n")

# 日志存储
request_logs = []


def ask_with_log(prompt, system="", max_tokens=300):
    """
    带日志记录的 API 调用

    除了返回结果，还记录：
    - 请求时间
    - prompt 内容
    - 响应内容
    - 耗时（毫秒）
    - token 消耗（输入 + 输出）
    """
    start_time = time.time()

    messages = [{"role": "user", "content": prompt}]
    kwargs = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    elapsed_ms = round((time.time() - start_time) * 1000)
    result_text = response.content[0].text

    # 记录日志
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "system": system[:50] + "..." if len(system) > 50 else system,
        "response": (
            result_text[:200] + "..." if len(result_text) > 200 else result_text
        ),
        "elapsed_ms": elapsed_ms,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "model": MODEL,
    }
    request_logs.append(log_entry)

    return result_text, log_entry


# 测试带日志的调用
# text, log = ask_with_log("1+1等于几？直接回答数字")
# print(f"回复: {text}")
# print(f"日志: {json.dumps(log, ensure_ascii=False, indent=2)}")


# ===========================================
# 4. 评估函数 — 自动跑测试
# ===========================================
# 核心思路：
# 1. 遍历评估集
# 2. 对每条 case 调 API 拿结果
# 3. 对比结果和期望，判断是否通过
# 4. 统计通过率 + 收集失败样本

# print(f"\n{'='*50}")
# print("=== 4. 自动化评估 ===\n")


def extract_with_prompt(text, task="extract_product"):
    """
    用 Prompt 约束法提取结构化数据（Day 1-2 的方法）
    这里封装一下，方便评估时统一调用
    """
    if task == "extract_product":
        prompt = f"""从以下文本中提取商品信息，直接返回 JSON（不要加 markdown 代码块标记，不要加任何解释）：

格式：{{"name": "商品名", "price": 数字, "color": "颜色", "storage": "存储容量"}}

文本：{text}"""
    elif task == "extract_resume":
        prompt = f"""从以下简历描述中提取信息，直接返回 JSON（不要加 markdown 代码块标记，不要加任何解释）：

格式：{{"name": "姓名", "experience_years": 数字, "skills": ["技能1", "技能2"], "education": "学历+学校"}}

文本：{text}"""
    else:
        return None

    result_text, log = ask_with_log(prompt)

    try:
        return json.loads(clean_markdown(result_text))
    except json.JSONDecodeError:
        return None


def check_result(actual, expected, check_fields):
    """
    检查实际输出是否符合期望

    三种匹配策略：
    1. 精确匹配（数字、布尔值）
    2. 包含匹配（字符串：期望值出现在实际值中）
    3. 列表匹配（检查期望的元素是否都在实际列表中）

    JS 类比：
    精确匹配 = expect(actual).toBe(expected)
    包含匹配 = expect(actual).toContain(expected)
    列表匹配 = expected.every(item => actual.includes(item))
    """
    if actual is None:
        return False, "API 返回为空或 JSON 解析失败"

    errors = []
    for field in check_fields:
        if field not in actual:
            errors.append(f"缺少字段: {field}")
            continue

        actual_val = actual[field]
        expected_val = expected.get(field)

        if expected_val is None:
            continue

        # 数字精确匹配
        if isinstance(expected_val, (int, float)):
            if actual_val != expected_val:
                errors.append(f"{field}: 期望 {expected_val}, 实际 {actual_val}")

        # 字符串包含匹配
        elif isinstance(expected_val, str):
            if expected_val not in str(actual_val):
                errors.append(
                    f"{field}: 期望包含 '{expected_val}', 实际 '{actual_val}'"
                )

        # 列表匹配（检查关键元素是否存在）
        elif isinstance(expected_val, list):
            if isinstance(actual_val, list):
                missing = [item for item in expected_val if item not in actual_val]
                if missing:
                    errors.append(f"{field}: 缺少 {missing}")
            else:
                errors.append(f"{field}: 期望列表, 实际 {type(actual_val).__name__}")

    if errors:
        return False, "; ".join(errors)
    return True, "通过"


def run_eval(cases, tag_filter=None):
    """
    运行评估集

    参数:
        cases: 评估用例列表
        tag_filter: 只跑包含该 tag 的 case（可选）

    返回:
        {
            "total": 总数,
            "passed": 通过数,
            "failed": 失败数,
            "pass_rate": 通过率,
            "avg_latency_ms": 平均延迟,
            "total_tokens": 总 token,
            "failures": [失败详情],
            "results": [所有结果],
        }

    JS 类比：
    类似 Jest 的 test runner，跑完一批 case 输出 summary
    """
    # 按 tag 过滤
    if tag_filter:
        cases = [c for c in cases if tag_filter in c.get("tags", [])]

    results = []
    failures = []
    total_tokens = 0
    total_latency = 0

    for case in cases:
        print(f"  评估 [{case['id']}] {case['input'][:30]}...")

        # 调用提取函数
        actual = extract_with_prompt(case["input"], case["task"])

        # 获取最近一条日志的指标
        log = request_logs[-1] if request_logs else {}
        latency = log.get("elapsed_ms", 0)
        tokens = log.get("total_tokens", 0)
        total_tokens += tokens
        total_latency += latency

        # 检查结果
        passed, reason = check_result(actual, case["expected"], case["check_fields"])

        result = {
            "id": case["id"],
            "input": case["input"],
            "expected": case["expected"],
            "actual": actual,
            "passed": passed,
            "reason": reason,
            "latency_ms": latency,
            "tokens": tokens,
        }
        results.append(result)

        if not passed:
            failures.append(result)
            print(f"    FAIL: {reason}")
        else:
            print(f"    PASS ({latency}ms, {tokens} tokens)")

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    summary = {
        "total": total_count,
        "passed": passed_count,
        "failed": total_count - passed_count,
        "pass_rate": (
            round(passed_count / total_count * 100, 1) if total_count > 0 else 0
        ),
        "avg_latency_ms": round(total_latency / total_count) if total_count > 0 else 0,
        "total_tokens": total_tokens,
        "failures": failures,
        "results": results,
    }

    return summary


# 跑评估（默认注释掉，取消注释运行）
# print("--- 跑商品提取评估 ---")
# summary = run_eval(eval_cases, tag_filter="商品提取")
# print(f"\n通过率: {summary['pass_rate']}% ({summary['passed']}/{summary['total']})")
# print(f"平均延迟: {summary['avg_latency_ms']}ms")
# print(f"总 token: {summary['total_tokens']}")


# ===========================================
# 5. 失败样本分析 — 找出问题在哪
# ===========================================
# 光知道"失败了"不够，要分析失败的模式

# print(f"\n{'='*50}")
# print("=== 5. 失败样本分析 ===\n")


def analyze_failures(summary):
    """
    分析失败样本，找出共性

    常见失败模式：
    1. JSON 解析失败 → prompt 不够严格，AI 夹带了文字
    2. 字段值错误   → AI 理解有误，需要更好的 prompt 或 few-shot
    3. 缺少字段     → schema 定义不清楚
    4. 边界 case    → 需要特殊处理（如信息不全）

    JS 类比：
    类似 Sentry 里的 error grouping — 把相似的错误归类
    """
    failures = summary.get("failures", [])
    if not failures:
        print("没有失败样本")
        return

    print(f"共 {len(failures)} 条失败:\n")
    for f in failures:
        print(f"  [{f['id']}] {f['input'][:40]}...")
        print(f"    期望: {json.dumps(f['expected'], ensure_ascii=False)}")
        print(
            f"    实际: {json.dumps(f['actual'], ensure_ascii=False) if f['actual'] else 'None'}"
        )
        print(f"    原因: {f['reason']}")
        print()


# ===========================================
# 6. 调试日志持久化 — 写入文件
# ===========================================
# 内存里的日志重启就没了，要写到文件里

# print(f"\n{'='*50}")
# print("=== 6. 日志持久化 ===\n")


def save_logs(logs, filename="debug_log.jsonl"):
    """
    保存日志到 JSONL 文件（每行一条 JSON）

    为什么用 JSONL 而不是 JSON？
    - JSON 需要一次性读取整个文件
    - JSONL 可以逐行追加，适合日志场景
    - 大文件也能流式处理

    JS 类比：
    类似 winston logger 写 JSON 格式日志
    """
    log_path = Path(__file__).parent / filename
    with open(log_path, "a", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
    print(f"已保存 {len(logs)} 条日志到 {log_path}")


def save_eval_report(summary, filename="eval_report.json"):
    """保存评估报告"""
    report_path = Path(__file__).parent / filename
    # 移除 results 中的大量详情，只保留摘要和失败样本
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": summary["total"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "pass_rate": summary["pass_rate"],
        "avg_latency_ms": summary["avg_latency_ms"],
        "total_tokens": summary["total_tokens"],
        "failures": summary["failures"],
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"评估报告已保存到 {report_path}")


# ===========================================
# 7. 回归测试 — 改 prompt 前后对比
# ===========================================
# 场景：你觉得 prompt 可以优化，改了一版
# 问题：新 prompt 在新 case 上好了，但旧 case 会不会退化？
# 方法：改之前先跑一遍评估，改之后再跑一遍，对比通过率

# print(f"\n{'='*50}")
# print("=== 7. 回归测试 ===\n")


def regression_test(cases, prompt_v1_fn, prompt_v2_fn, tag_filter=None):
    """
    回归测试：对比两个版本的 prompt

    参数:
        cases: 评估用例
        prompt_v1_fn: 旧版提取函数
        prompt_v2_fn: 新版提取函数
        tag_filter: 过滤 tag

    返回对比结果

    JS 类比：
    类似 A/B 测试 — 同一批用户分别用 v1 和 v2，看哪个效果好
    """
    if tag_filter:
        cases = [c for c in cases if tag_filter in c.get("tags", [])]

    v1_results = []
    v2_results = []

    for case in cases:
        # V1
        actual_v1 = prompt_v1_fn(case["input"], case["task"])
        passed_v1, _ = check_result(actual_v1, case["expected"], case["check_fields"])
        v1_results.append(passed_v1)

        # V2
        actual_v2 = prompt_v2_fn(case["input"], case["task"])
        passed_v2, _ = check_result(actual_v2, case["expected"], case["check_fields"])
        v2_results.append(passed_v2)

    v1_pass = sum(v1_results)
    v2_pass = sum(v2_results)
    total = len(cases)

    print(f"V1 通过率: {v1_pass}/{total} ({round(v1_pass/total*100, 1)}%)")
    print(f"V2 通过率: {v2_pass}/{total} ({round(v2_pass/total*100, 1)}%)")

    # 找出退化的 case（V1 通过但 V2 没通过）
    regressions = []
    for i, case in enumerate(cases):
        if v1_results[i] and not v2_results[i]:
            regressions.append(case["id"])

    if regressions:
        print(f"\n!! 退化警告: 以下 case 在 V2 中失败: {regressions}")
    else:
        print("\n没有退化，V2 安全")

    return {
        "v1_pass_rate": round(v1_pass / total * 100, 1),
        "v2_pass_rate": round(v2_pass / total * 100, 1),
        "regressions": regressions,
    }


# --- 回归测试示例 ---
# 假设我们优化了商品提取的 prompt（加了 few-shot）


def extract_v2(text, task="extract_product"):
    """
    V2 版本：加了 few-shot 示例
    理论上更稳定，但需要回归测试确认
    """
    if task == "extract_product":
        prompt = f"""从以下文本中提取商品信息，直接返回 JSON（不要加 markdown 代码块标记）。

示例：
输入：MacBook Pro 14 寸 M3 Pro 深空黑 14999 元
输出：{{"name": "MacBook Pro 14 寸 M3 Pro", "price": 14999, "color": "深空黑", "storage": ""}}

现在提取：
输入：{text}
输出："""
    elif task == "extract_resume":
        prompt = f"""从以下简历描述中提取信息，直接返回 JSON（不要加 markdown 代码块标记）。

示例：
输入：小明，2年 Java 开发，熟悉 Spring Boot，本科毕业于北京大学
输出：{{"name": "小明", "experience_years": 2, "skills": ["Java", "Spring Boot"], "education": "本科 北京大学"}}

现在提取：
输入：{text}
输出："""
    else:
        return None

    result_text, _ = ask_with_log(prompt)
    try:
        return json.loads(clean_markdown(result_text))
    except json.JSONDecodeError:
        return None


# 跑回归测试（默认注释掉）
# print("--- 回归测试: V1 vs V2 ---")
# regression_test(eval_cases, extract_with_prompt, extract_v2, tag_filter="简历提取")


# ===========================================
# 8. 完整评估流程演示
# ===========================================

# print(f"\n{'='*50}")
# print("=== 8. 完整评估流程 ===\n")


def full_eval_demo():
    """
    完整评估流程：
    1. 加载评估集
    2. 跑评估
    3. 分析失败
    4. 保存日志和报告
    """
    print("Step 1: 加载评估集")
    print(f"  共 {len(eval_cases)} 条用例\n")

    print("Step 2: 跑商品提取评估")
    summary = run_eval(eval_cases, tag_filter="商品提取")
    print(f"\n  通过率: {summary['pass_rate']}%")
    print(f"  平均延迟: {summary['avg_latency_ms']}ms")
    print(f"  总 token: {summary['total_tokens']}\n")

    print("Step 3: 分析失败样本")
    analyze_failures(summary)

    print("Step 4: 保存日志和报告")
    save_logs(request_logs)
    save_eval_report(summary)

    print("\n完成！")


# 取消注释运行完整评估流程
# full_eval_demo()


# ===========================================
# 总结
# ===========================================

# print(f"\n{'='*50}")
# print("=== 总结 ===")
# print("""
# AI 应用评估与调试的核心：
#
# 1. 评估集     — 固定输入 + 期望输出，存成 JSON，版本控制
# 2. 自动评估   — run_eval() 批量跑 case，统计通过率
# 3. 调试日志   — 每次 API 调用记录 prompt/response/token/耗时
# 4. 失败分析   — 找出失败模式，针对性优化 prompt
# 5. 回归测试   — 改 prompt 前后对比，确保不退化
# 6. 指标关注   — 正确率、延迟、token 消耗、成本
#
# 关键心态：
# - AI 应用不是"写完就行"，是"写完 + 评估 + 迭代"
# - 每次改 prompt 都要跑回归
# - 日志是你最好的调试工具
#
# 下一课：Day 4 LangChain 基础
# """)
