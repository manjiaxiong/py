# ===========================================
# 练习 3：RAG 优化（对应 Day 3）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 03_rag_optimization.py / 03_rag_optimization.md
# ===========================================

import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask
import chromadb


# --- 题目 1: chunk_size 对比实验 ---

# TODO 1.1: 实现 chunk_by_size 函数（和练习 1 一样）
def chunk_by_size(text, chunk_size=300, overlap=50):
    """按固定字数分块，带重叠"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# TODO 1.2: 对比实验
# 用 200 / 500 / 1000 三种大小对同一文档分块
# 分别建索引、检索同一个 query、对比距离值
# 结论：哪个 chunk_size 检索结果距离最小（最相关）？


# --- 题目 2: 相似度阈值过滤 ---

# TODO 2.1: 封装带阈值的 RAG 函数
def rag_with_threshold(collection, query, client, model, n_results=3, threshold=1.5):
    """
    带阈值过滤的 RAG

    流程：
    1. 检索 n_results 条结果
    2. 过滤距离 >= threshold 的结果
    3. 如果没有通过阈值的，返回"文档中未找到相关信息"
    4. 否则拼接上下文，调 LLM 回答

    JS 类比：
    async function ragQuery(query, { nResults, threshold }) {
        const results = await search(query, nResults);
        const relevant = results.filter(r => r.distance < threshold);
        if (relevant.length === 0) return "没有找到相关信息";
        return await askAI(relevant, query);
    }
    """
    # TODO: 实现带阈值的 RAG
    pass


# 测试
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
# chroma = chromadb.Client()
# collection = chroma.create_collection(name="threshold_test")
#
# # 先索引一些文档
# # TODO: 读 sample_docs 的文件，分块，存入 collection
#
# # 测试：文档中有的问题 vs 文档中没有的问题
# questions = ["React 的 Hooks 有哪些？", "量子计算的原理是什么？"]
# for q in questions:
#     answer = rag_with_threshold(collection, q, client_ai, MODEL, threshold=1.5)
#     print(f"Q: {q}")
#     print(f"A: {answer}")


# --- 题目 3: 引用来源 ---

# TODO 3.1: 建索引时存入来源信息（source, chunk_index, preview）
# TODO 3.2: 检索时返回来源列表
# TODO 3.3: 让 AI 在回答末尾标注引用来源
# prompt 模板中加上：回答末尾标注引用来源（文件名）


# --- 题目 4: RAG 评估 ---

# TODO 4.1: 定义评估集（至少 3 条 QA）
eval_set = [
    {
        "question": "___",
        "expected_source": "___",
        "expected_keywords": ["___"],
    },
    # TODO: 再写 2+ 条
]


# TODO 4.2: 运行评估
def run_eval(collection, client, model, eval_set, n_results=3):
    """
    运行 RAG 评估，分开评估检索和生成

    返回:
        {
            "retrieval_hit_rate": 命中率 (0-1),
            "generation_pass_rate": 通过率 (0-1),
            "details": [每条的详细结果],
        }
    """
    retrieval_hits = 0
    generation_hits = 0
    details = []

    for item in eval_set:
        # 检索
        results = collection.query(query_texts=[item["question"]], n_results=n_results)
        retrieved_sources = [m["source"] for m in results["metadatas"][0]]

        # 检索评估：期望来源是否在 top-k 中
        retrieval_hit = item["expected_source"] in retrieved_sources
        if retrieval_hit:
            retrieval_hits += 1

        # TODO: 生成评估 — 调 LLM 回答，检查关键词命中
        # generation_hit = ...

        details.append({
            "question": item["question"],
            "retrieval_hit": retrieval_hit,
            # TODO: 加 generation_hit
        })

    total = len(eval_set)
    return {
        "retrieval_hit_rate": retrieval_hits / total,
        "generation_pass_rate": generation_hits / total,
        "details": details,
    }


# TODO 4.3: 调用 run_eval 并打印结果
# result = run_eval(collection, client_ai, MODEL, eval_set)
# print(f"检索命中率: {result['retrieval_hit_rate']:.0%}")
# print(f"生成通过率: {result['generation_pass_rate']:.0%}")
# for d in result["details"]:
#     print(f"  {d['question']}: 检索={'✅' if d['retrieval_hit'] else '❌'}")


# --- 题目 5: 思考题 ---

# TODO 5.1: 以下场景选择什么优化方案？
# 场景 1：用户问了一个完全无关的问题，AI 基于不相关内容编造了答案
# 方案：___
#
# 场景 2：检索结果总是包含不相关的文档，回答质量差
# 方案：___（从 chunk_size / top_k / rerank 中选）
#
# 场景 3：回答总是很简短，漏掉重要信息
# 方案：___
