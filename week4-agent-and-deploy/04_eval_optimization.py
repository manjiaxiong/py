# ===========================================
# Day 4: 评估与优化 — 项目级质量保障
# ===========================================
# 评估 = 给 AI 系统打分
# 优化 = 根据评估结果调整参数
#
# 类比：
# 代码有单元测试 → AI 系统有评估集
# 前端有 Lighthouse → AI 有 latency/cost/accuracy 指标
#
# 前端类比：
# 评估集  = E2E 测试用例
# 回归测试 = 改了 prompt 后跑一遍确保没破坏之前的
# 调优    = 性能优化（减少 bundle size → 减少 token）
# ===========================================

import sys
import json
import time
import functools
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

client, MODEL = get_client(Path(__file__).parent / ".env")


# ===========================================
# 1. 项目级评估体系
# ===========================================
# 为什么需要评估？
# - 改了 prompt → 之前能回答的问题突然答错了（回归 bug）
# - 加了新工具 → Agent 反而更慢了
# - 换了模型 → 不确定效果变好还是变差
#
# 评估集结构：
# {
#   "id": "case_001",
#   "input": "用户输入",
#   "expected_output": "期望输出（关键词）",
#   "tags": ["agent", "tool_use"],
# }
#
# JS 类比：
# describe('AI Agent', () => {
#   test('should answer math questions', () => { ... });
#   test('should use calculator tool', () => { ... });
# });

# 定义评估集
EVAL_CASES = [
    {
        "id": "case_001",
        "input": "把 Hello World 翻译成中文",
        "expected_keywords": ["你好", "世界"],
        "tags": ["translation", "simple"],
    },
    {
        "id": "case_002",
        "input": "Python 列表推导式怎么写？给个例子",
        "expected_keywords": ["for", "in", "["],
        "tags": ["code", "python"],
    },
    {
        "id": "case_003",
        "input": "解释什么是 RESTful API，用一句话",
        "expected_keywords": ["REST", "HTTP", "资源"],
        "tags": ["concept", "api"],
    },
    {
        "id": "case_004",
        "input": "1+1等于多少",
        "expected_keywords": ["2"],
        "tags": ["math", "simple"],
    },
    {
        "id": "case_005",
        "input": "FastAPI 和 Flask 有什么区别？",
        "expected_keywords": ["异步", "性能", "类型"],
        "tags": ["comparison", "python"],
    },
]


def run_eval(eval_cases, client, model, system_prompt=""):
    """
    运行评估

    参数:
        eval_cases: 评估集列表
        client: AI 客户端
        model: 模型名称
        system_prompt: 系统提示词

    返回:
        {
            "total": 总数,
            "passed": 通过数,
            "pass_rate": 通过率,
            "details": [每条详情],
            "total_latency": 总耗时,
            "avg_latency": 平均耗时,
        }
    """
    passed = 0
    details = []
    total_latency = 0

    for case in eval_cases:
        start = time.time()
        answer = ask(client, model, case["input"], system=system_prompt, max_tokens=300)
        latency = time.time() - start
        total_latency += latency

        # 关键词匹配
        matched = [kw for kw in case["expected_keywords"] if kw.lower() in answer.lower()]
        is_pass = len(matched) >= max(1, len(case["expected_keywords"]) // 2)
        if is_pass:
            passed += 1

        details.append({
            "id": case["id"],
            "input": case["input"],
            "answer_preview": answer[:80] + "..." if len(answer) > 80 else answer,
            "passed": is_pass,
            "matched_keywords": matched,
            "expected_keywords": case["expected_keywords"],
            "latency_ms": round(latency * 1000, 1),
            "tags": case.get("tags", []),
        })

    total = len(eval_cases)
    return {
        "total": total,
        "passed": passed,
        "pass_rate": passed / total if total > 0 else 0,
        "details": details,
        "total_latency_ms": round(total_latency * 1000, 1),
        "avg_latency_ms": round(total_latency / total * 1000, 1) if total > 0 else 0,
    }


print("=== Section 1: 评估体系 ===")
print(f"评估集: {len(EVAL_CASES)} 条用例\n")

result = run_eval(EVAL_CASES, client, MODEL)
print(f"通过率: {result['passed']}/{result['total']} ({result['pass_rate']:.0%})")
print(f"平均延迟: {result['avg_latency_ms']:.0f}ms")
for d in result["details"]:
    print(f"  {'✅' if d['passed'] else '❌'} [{d['id']}] {d['input'][:30]}... ({d['latency_ms']:.0f}ms)")


# ===========================================
# 2. 失败任务分析
# ===========================================
# 失败了不可怕，关键是分类原因
#
# 常见失败原因：
# 1. Prompt 不够清晰 → 改 prompt
# 2. 工具描述有歧义 → 改 tool description
# 3. 检索结果不相关 → 调 RAG 参数
# 4. 模型能力不足 → 换模型
# 5. 上下文太长截断 → 减少 context
#
# JS 类比：
# Sentry 错误分类 → AI 失败分类
# 前端 bug = 逻辑错误 / 样式错误 / 网络错误
# AI bug = prompt 错误 / 工具错误 / 检索错误 / 模型错误

def analyze_failures(eval_result):
    """
    分析失败用例

    返回:
        {"failures": [...], "categories": {"prompt": N, "model": N, ...}}
    """
    failures = [d for d in eval_result["details"] if not d["passed"]]

    if not failures:
        print("  🎉 没有失败用例！")
        return {"failures": [], "categories": {}}

    # 简单分类（实际项目中会更复杂）
    categories = {}
    for f in failures:
        # 根据 tags 猜测失败原因
        if "simple" in f["tags"]:
            category = "model"  # 简单问题都错 → 模型问题
        elif len(f["matched_keywords"]) == 0:
            category = "prompt"  # 完全没匹配 → prompt 问题
        else:
            category = "partial"  # 部分匹配 → 需要细看

        categories[category] = categories.get(category, 0) + 1
        f["failure_category"] = category

    return {"failures": failures, "categories": categories}


# print("\n=== Section 2: 失败分析 ===")
# analysis = analyze_failures(result)
# if analysis["failures"]:
#     print(f"失败用例: {len(analysis['failures'])} 条")
#     print(f"分类: {analysis['categories']}")
#     for f in analysis["failures"]:
#         print(f"  ❌ {f['id']}: {f['input'][:30]}... → {f['failure_category']}")


# ===========================================
# 3. 多轮调优对比
# ===========================================
# 优化策略：改 prompt → 跑评估 → 对比 → 选最优
#
# JS 类比：
# A/B 测试 — 同一个评估集，不同配置，对比效果

PROMPTS = {
    "baseline": "",  # 无 system prompt
    "concise": "你是一个简洁高效的助手，用中文回答，回答控制在 50 字以内。",
    "detailed": "你是一个专业技术助手，用中文详细回答技术问题，确保包含关键术语和示例。",
}


def compare_prompts(eval_cases, client, model, prompt_configs):
    """
    对比不同 prompt 配置的效果

    参数:
        eval_cases: 评估集
        prompt_configs: {名称: system_prompt}

    返回:
        {名称: eval_result}
    """
    results = {}
    for name, system_prompt in prompt_configs.items():
        print(f"\n  🔄 评估配置: {name}...")
        result = run_eval(eval_cases, client, model, system_prompt=system_prompt)
        results[name] = result
        print(f"     通过率: {result['pass_rate']:.0%}, 平均延迟: {result['avg_latency_ms']:.0f}ms")
    return results


# print("\n=== Section 3: 多轮调优对比 ===")
# comparison = compare_prompts(EVAL_CASES, client, MODEL, PROMPTS)
#
# print("\n  对比汇总:")
# print("  ┌──────────┬──────────┬──────────┐")
# print("  │ 配置      │ 通过率    │ 平均延迟  │")
# print("  ├──────────┼──────────┼──────────┤")
# for name, r in comparison.items():
#     print(f"  │ {name:<8} │ {r['pass_rate']:<8.0%} │ {r['avg_latency_ms']:<8.0f}ms │")
# print("  └──────────┴──────────┴──────────┘")


# ===========================================
# 4. 延迟和成本优化
# ===========================================
# 装饰器：记录每次调用的延迟和 token 估算
#
# JS 类比：
# const trackPerformance = (fn) => async (...args) => {
#   const start = performance.now();
#   const result = await fn(...args);
#   const duration = performance.now() - start;
#   metrics.push({ duration, timestamp: Date.now() });
#   return result;
# };

call_metrics = []


def track_latency(fn):
    """
    延迟追踪装饰器

    JS 类比：
    const withTiming = (fn) => (...args) => {
        const t0 = Date.now();
        const result = fn(...args);
        console.log(`${fn.name}: ${Date.now() - t0}ms`);
        return result;
    }
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        latency = time.time() - start

        call_metrics.append({
            "function": fn.__name__,
            "latency_ms": round(latency * 1000, 1),
            "timestamp": time.time(),
        })
        return result
    return wrapper


# 给 ask 函数加上延迟追踪
@track_latency
def ask_tracked(client, model, prompt, **kwargs):
    return ask(client, model, prompt, **kwargs)


# print("\n=== Section 4: 延迟追踪 ===")
# # 做几次调用
# for q in ["你好", "Python 是什么？", "1+1"]:
#     ask_tracked(client, MODEL, q, max_tokens=50)
#
# # 查看统计
# if call_metrics:
#     latencies = [m["latency_ms"] for m in call_metrics]
#     print(f"  调用次数: {len(latencies)}")
#     print(f"  平均延迟: {sum(latencies)/len(latencies):.0f}ms")
#     print(f"  最慢: {max(latencies):.0f}ms")
#     print(f"  最快: {min(latencies):.0f}ms")


# ===========================================
# 5. 调优报告生成
# ===========================================
# 把评估和对比结果输出成 Markdown 报告

def generate_report(eval_result, comparison=None, output_path=None):
    """
    生成调优报告

    参数:
        eval_result: 基线评估结果
        comparison: 多配置对比结果（可选）
        output_path: 输出文件路径（可选）

    返回:
        Markdown 格式报告字符串
    """
    lines = []
    lines.append("# AI 系统评估与调优报告\n")
    lines.append(f"- 评估时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 评估用例: {eval_result['total']} 条")
    lines.append(f"- 基线通过率: {eval_result['pass_rate']:.0%}")
    lines.append(f"- 平均延迟: {eval_result['avg_latency_ms']:.0f}ms\n")

    # 用例详情
    lines.append("## 用例详情\n")
    lines.append("| ID | 输入 | 结果 | 延迟 |")
    lines.append("|---|---|---|---|")
    for d in eval_result["details"]:
        status = "PASS" if d["passed"] else "FAIL"
        lines.append(f"| {d['id']} | {d['input'][:25]}... | {status} | {d['latency_ms']:.0f}ms |")

    # 对比（如果有）
    if comparison:
        lines.append("\n## 配置对比\n")
        lines.append("| 配置 | 通过率 | 平均延迟 |")
        lines.append("|---|---|---|")
        for name, r in comparison.items():
            lines.append(f"| {name} | {r['pass_rate']:.0%} | {r['avg_latency_ms']:.0f}ms |")

    # 建议
    lines.append("\n## 优化建议\n")
    if eval_result["pass_rate"] < 0.7:
        lines.append("- 通过率偏低，建议优化 system prompt 或换更强模型")
    if eval_result["avg_latency_ms"] > 3000:
        lines.append("- 延迟偏高，建议减少 max_tokens 或使用更快模型")
    if eval_result["pass_rate"] >= 0.7 and eval_result["avg_latency_ms"] <= 3000:
        lines.append("- 效果良好，可以继续增加评估用例覆盖更多场景")

    report = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"  📄 报告已保存: {output_path}")

    return report


print("\n=== Section 5: 调优报告 ===")
report = generate_report(result, output_path=Path(__file__).parent / "eval_report.md")
print("报告预览:")
print(report[:500] + "...")
