# ===========================================
# eval_runner.py — Docs Copilot 评估脚本
# ===========================================
# 评估 RAG 系统的检索和生成质量
# 用法: python week3-project/eval_runner.py
#
# 评估分两部分：
# 1. 检索评估：检索到的文档是否来自期望的来源？
# 2. 生成评估：AI 回答中是否包含期望的关键词？
# ===========================================

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag import RAGPipeline


def load_cases(path):
    """加载评估集"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_retrieval(sources, expected_source):
    """
    检索评估：期望来源是否在结果中？

    返回: (hit: bool, matched_source: str or None)
    """
    if expected_source is None:
        # 期望无来源（无关问题），检查结果是否确实无匹配
        return True, None

    available_sources = [s.get("source", "") for s in sources]
    if expected_source in available_sources:
        return True, expected_source

    # 部分匹配：文件名包含
    for src in available_sources:
        if expected_source.split(".")[0] in src:
            return True, src

    return False, None


def check_generation(answer, expected_keywords):
    """
    生成评估：回答中是否包含期望关键词？

    返回: (pass: bool, matched: list[str])
    """
    if not expected_keywords:
        return True, []

    matched = [kw for kw in expected_keywords if kw.lower() in answer.lower()]
    # 命中一半以上就算通过
    passed = len(matched) >= max(1, len(expected_keywords) // 2)
    return passed, matched


def run_eval(cases, pipeline, n_results=3):
    """
    运行完整评估

    返回:
        {
            "retrieval": {"hit": int, "total": int, "rate": float},
            "generation": {"pass": int, "total": int, "rate": float},
            "details": [...]
        }
    """
    retrieval_hits = 0
    generation_passes = 0
    details = []

    # 过滤掉拒答测试（不参与生成评估）
    eval_cases = [c for c in cases if c.get("expected_source") is not None]
    reject_cases = [c for c in cases if c.get("expected_source") is None]

    print(f"评估集: {len(cases)} 条测试")
    print(f"  检索+生成: {len(eval_cases)} 条")
    print(f"  拒答测试: {len(reject_cases)} 条")
    print("=" * 60)

    for i, item in enumerate(eval_cases):
        q = item["question"]
        expected_src = item.get("expected_source")
        expected_kws = item.get("expected_keywords", [])

        # RAG 问答
        result = pipeline.ask(q, n_results=n_results)
        answer = result["answer"]
        sources = result["sources"]

        # 检索评估
        ret_hit, matched_src = check_retrieval(sources, expected_src)
        if ret_hit:
            retrieval_hits += 1

        # 生成评估
        gen_pass, matched_kws = check_generation(answer, expected_kws)
        if gen_pass:
            generation_passes += 1

        details.append({
            "id": item["id"],
            "question": q,
            "tags": item.get("tags", []),
            "retrieval_hit": ret_hit,
            "matched_source": matched_src,
            "generation_pass": gen_pass,
            "matched_keywords": matched_kws,
            "answer_preview": answer[:80] + "..." if len(answer) > 80 else answer,
        })

        # 打印
        print(f"\n[{i+1}] {q}")
        print(f"  检索: {'✅' if ret_hit else '❌'} (期望: {expected_src}, 实际: {matched_src})")
        if expected_kws:
            print(f"  生成: {'✅' if gen_pass else '❌'} (关键词: {matched_kws}/{expected_kws})")
        print(f"  回答: {answer[:100]}...")

    # 拒答测试
    print(f"\n{'=' * 60}")
    print("拒答测试:")
    for item in reject_cases:
        q = item["question"]
        result = pipeline.ask(q, n_results=n_results)
        answer = result["answer"]
        # 拒答测试：回答中应包含"无法回答"或"未找到"
        is_rejected = any(kw in answer for kw in ["无法回答", "未找到", "未提及", "没有相关信息"])
        print(f"  [{ '✅' if is_rejected else '❌' }] {q}")
        print(f"    回答: {answer[:80]}...")

    # 汇总
    total_eval = len(eval_cases)
    retrieval_rate = retrieval_hits / total_eval if total_eval > 0 else 0
    generation_rate = generation_passes / total_eval if total_eval > 0 else 0

    print(f"\n{'=' * 60}")
    print(f"评估汇总")
    print(f"  检索命中率: {retrieval_hits}/{total_eval} ({retrieval_rate:.0%})")
    print(f"  生成通过率: {generation_passes}/{total_eval} ({generation_rate:.0%})")
    print()
    print("优化建议:")
    if retrieval_rate < 0.7:
        print("  - 检索命中率低 → 调整 chunk_size、换 embedding 模型、加 rerank")
    if generation_rate < 0.7:
        print("  - 生成通过率低 → 优化 prompt 模板、增加上下文、调整 top_k")
    if retrieval_rate >= 0.7 and generation_rate >= 0.7:
        print("  - 效果不错！可以尝试更复杂的问题")

    return {
        "retrieval": {"hit": retrieval_hits, "total": total_eval, "rate": retrieval_rate},
        "generation": {"pass": generation_passes, "total": total_eval, "rate": generation_rate},
        "details": details,
    }


if __name__ == "__main__":
    # 加载评估集
    cases_path = Path(__file__).parent / "eval_cases.json"
    cases = load_cases(cases_path)

    # 初始化 pipeline
    print("初始化 RAG Pipeline...")
    pipeline = RAGPipeline().init(Path(__file__).parent / ".env")

    # 如果向量库为空，先索引文档
    if pipeline.collection.count() == 0:
        docs_dir = Path(__file__).parent / "docs"
        if docs_dir.exists():
            print("索引文档...")
            result = pipeline.index_directory(docs_dir)
            print(f"  索引完成: {result['total_chunks']} 个块")
        else:
            print("错误: docs/ 目录不存在，请先放置文档文件")
            sys.exit(1)

    # 运行评估
    result = run_eval(cases, pipeline)

    # 保存结果
    output_path = Path(__file__).parent / "eval_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n评估结果已保存到: {output_path}")
