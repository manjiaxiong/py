# ===========================================
# 练习 4：评估与优化（对应 Day 4）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 04_eval_optimization.py / 04_eval_optimization.md
# ===========================================

import sys
import time
import json
import functools
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

client, MODEL = get_client(Path(__file__).parent / ".env")


# --- 题目 1: 设计评估集 ---

# TODO 1.1: 设计 5 条评估用例
eval_cases = [
    {
        "id": "eval_001",
        "input": "什么是 RAG？",
        "expected_keywords": ["检索", "增强", "生成"],
        "tags": ["concept"],
    },
    {
        "id": "eval_002",
        "input": "Python 的 list 和 tuple 有什么区别？",
        "expected_keywords": ["可变", "不可变"],
        "tags": ["python"],
    },
    {
        "id": "eval_003",
        "input": "解释 REST API 中 GET 和 POST 的区别",
        "expected_keywords": ["GET", "POST", "获取", "提交"],
        "tags": ["api"],
    },
    {
        "id": "eval_004",
        "input": "Docker 的主要优势是什么？",
        "expected_keywords": ["容器", "一致", "隔离"],
        "tags": ["devops"],
    },
    {
        "id": "eval_005",
        "input": "1 + 2 * 3 等于多少",
        "expected_keywords": ["7"],
        "tags": ["math"],
    },
]

print("=== 题目 1: 评估集 ===")
print(f"共 {len(eval_cases)} 条用例:")
for c in eval_cases:
    print(f"  [{c['id']}] {c['input'][:30]}... | 关键词: {c['expected_keywords']}")


# --- 题目 2: 运行评估 ---

# TODO 2.1: 实现评估函数
def run_eval(cases, client, model, system_prompt=""):
    """
    运行评估，返回通过率和详情
    """
    passed = 0
    details = []
    total_latency = 0

    for case in cases:
        start = time.time()
        answer = ask(client, model, case["input"], system=system_prompt, max_tokens=200)
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
            "passed": is_pass,
            "matched": matched,
            "expected": case["expected_keywords"],
            "latency_ms": round(latency * 1000, 1),
            "answer_preview": answer[:60] + "...",
        })

    total = len(cases)
    return {
        "total": total,
        "passed": passed,
        "pass_rate": passed / total if total > 0 else 0,
        "avg_latency_ms": round(total_latency / total * 1000, 1) if total > 0 else 0,
        "details": details,
    }


print("\n=== 题目 2: 运行评估 ===")
result = run_eval(eval_cases, client, MODEL)
print(f"通过率: {result['passed']}/{result['total']} ({result['pass_rate']:.0%})")
print(f"平均延迟: {result['avg_latency_ms']:.0f}ms")
for d in result["details"]:
    status = "✅" if d["passed"] else "❌"
    print(f"  {status} [{d['id']}] {d['input'][:25]}... ({d['latency_ms']:.0f}ms) 匹配: {d['matched']}")


# --- 题目 3: 延迟和成本统计 ---

# TODO 3.1: 实现延迟追踪装饰器
metrics = []


def track_latency(fn):
    """延迟追踪装饰器"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        ms = round((time.time() - start) * 1000, 1)
        metrics.append({"fn": fn.__name__, "ms": ms})
        return result
    return wrapper


@track_latency
def ask_tracked(client, model, prompt, **kwargs):
    return ask(client, model, prompt, **kwargs)


# 做几次调用
print("\n=== 题目 3: 延迟统计 ===")
for q in ["你好", "1+1", "什么是 API？"]:
    ask_tracked(client, MODEL, q, max_tokens=50)

if metrics:
    latencies = [m["ms"] for m in metrics]
    print(f"  调用次数: {len(latencies)}")
    print(f"  平均延迟: {sum(latencies)/len(latencies):.0f}ms")
    print(f"  最快: {min(latencies):.0f}ms")
    print(f"  最慢: {max(latencies):.0f}ms")


# --- 题目 4: 调优对比 ---

# TODO 4.1: 对比不同 system prompt 的效果
configs = {
    "baseline": "",
    "concise": "你是一个技术助手，用中文简洁回答，30字以内。",
    "detailed": "你是一个资深技术专家，用中文详细回答，确保包含核心概念和关键术语。",
}

print("\n=== 题目 4: 调优对比 ===")
comparison = {}
for name, prompt in configs.items():
    print(f"\n  配置: {name}")
    r = run_eval(eval_cases, client, MODEL, system_prompt=prompt)
    comparison[name] = r
    print(f"  通过率: {r['pass_rate']:.0%}, 延迟: {r['avg_latency_ms']:.0f}ms")

# 汇总表
print("\n  ┌──────────┬──────────┬──────────┐")
print("  │ 配置      │ 通过率    │ 平均延迟  │")
print("  ├──────────┼──────────┼──────────┤")
for name, r in comparison.items():
    print(f"  │ {name:<8} │ {r['pass_rate']:<8.0%} │ {r['avg_latency_ms']:<8.0f}ms │")
print("  └──────────┴──────────┴──────────┘")

# 选最优
best = max(comparison.items(), key=lambda x: x[1]["pass_rate"])
print(f"\n  推荐配置: {best[0]}（通过率 {best[1]['pass_rate']:.0%}）")
