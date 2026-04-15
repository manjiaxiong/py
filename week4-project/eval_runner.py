# ===========================================
# eval_runner.py — AI Workflow Assistant 评估脚本
# ===========================================
# 评估工作流的规划和执行质量
# 用法: python week4-project/eval_runner.py
# ===========================================

import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.append(str(Path(__file__).resolve().parent.parent))

import workflow


def load_cases(path):
    """加载评估集"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_tools(step_results, expected_tools):
    """
    工具评估：期望工具是否被调用？

    返回: (hit: bool, used_tools: list)
    """
    used_tools = [r.get("tool", "") for r in step_results]

    if not expected_tools:
        return True, used_tools

    hits = sum(1 for et in expected_tools if any(et in ut for ut in used_tools))
    return hits >= len(expected_tools) // 2 + 1 or hits == len(expected_tools), used_tools


def check_keywords(final_result, expected_keywords):
    """
    关键词评估：结果中是否包含期望关键词？

    返回: (pass: bool, matched: list)
    """
    if not expected_keywords:
        return True, []

    matched = [kw for kw in expected_keywords if kw.lower() in final_result.lower()]
    passed = len(matched) >= max(1, len(expected_keywords) // 2)
    return passed, matched


def run_eval(cases, max_steps=5):
    """
    运行完整评估

    返回: {tool_rate, keyword_rate, details, total_latency}
    """
    tool_hits = 0
    keyword_hits = 0
    details = []
    total_latency = 0

    print(f"评估集: {len(cases)} 条测试")
    print("=" * 60)

    for i, case in enumerate(cases):
        task = case["task_description"]
        expected_tools = case.get("expected_tools", [])
        expected_kws = case.get("expected_keywords", [])

        print(f"\n[{i+1}] {task}")

        start = time.time()
        try:
            result = workflow.run_task(task, max_steps=max_steps)
            latency = time.time() - start
            total_latency += latency

            step_results = result.get("step_results", [])
            final_result = result.get("final_result", "")

            # 工具评估
            tool_hit, used_tools = check_tools(step_results, expected_tools)
            if tool_hit:
                tool_hits += 1

            # 关键词评估
            kw_pass, matched_kws = check_keywords(final_result, expected_kws)
            if kw_pass:
                keyword_hits += 1

            details.append({
                "id": case["id"],
                "task": task,
                "tags": case.get("tags", []),
                "tool_hit": tool_hit,
                "used_tools": used_tools,
                "expected_tools": expected_tools,
                "keyword_pass": kw_pass,
                "matched_keywords": matched_kws,
                "expected_keywords": expected_kws,
                "steps_count": len(step_results),
                "latency_s": round(latency, 1),
                "result_preview": final_result[:80] + "..." if len(final_result) > 80 else final_result,
            })

            print(f"  工具: {'✅' if tool_hit else '❌'} (期望: {expected_tools}, 实际: {used_tools})")
            print(f"  关键词: {'✅' if kw_pass else '❌'} ({matched_kws}/{expected_kws})")
            print(f"  步骤: {len(step_results)}, 耗时: {latency:.1f}s")
            print(f"  结果: {final_result[:80]}...")

        except Exception as e:
            latency = time.time() - start
            total_latency += latency
            print(f"  ❌ 执行失败: {e}")
            details.append({
                "id": case["id"],
                "task": task,
                "tool_hit": False,
                "keyword_pass": False,
                "error": str(e),
            })

    # 汇总
    total = len(cases)
    tool_rate = tool_hits / total if total > 0 else 0
    keyword_rate = keyword_hits / total if total > 0 else 0

    print(f"\n{'='*60}")
    print(f"评估汇总")
    print(f"  工具命中率: {tool_hits}/{total} ({tool_rate:.0%})")
    print(f"  关键词通过率: {keyword_hits}/{total} ({keyword_rate:.0%})")
    print(f"  总耗时: {total_latency:.1f}s, 平均: {total_latency/total:.1f}s/条")
    print()

    if tool_rate < 0.7:
        print("优化建议: 工具命中率低 → 优化 plan 的 prompt，让 LLM 更准确选择工具")
    if keyword_rate < 0.7:
        print("优化建议: 关键词通过率低 → 优化 summarize 的 prompt，确保包含关键信息")
    if tool_rate >= 0.7 and keyword_rate >= 0.7:
        print("效果良好，可以增加更复杂的评估用例")

    return {
        "tool_rate": tool_rate,
        "keyword_rate": keyword_rate,
        "total": total,
        "tool_hits": tool_hits,
        "keyword_hits": keyword_hits,
        "total_latency_s": round(total_latency, 1),
        "details": details,
    }


if __name__ == "__main__":
    # 初始化
    print("初始化 Workflow...")
    workflow.init(Path(__file__).parent / ".env")

    # 加载评估集
    cases_path = Path(__file__).parent / "eval_cases.json"
    cases = load_cases(cases_path)

    # 运行评估
    result = run_eval(cases, max_steps=5)

    # 保存结果
    output_path = Path(__file__).parent / "eval_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n评估结果已保存到: {output_path}")
