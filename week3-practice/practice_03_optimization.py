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

def chunk_by_size(text, chunk_size=300, overlap=50):
    """按固定字数分块，带重叠"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# 对比实验：用不同 chunk_size 对同一文档分块，对比检索效果
def run_chunk_experiment(doc_text, query="React Hooks 有哪些？"):
    """
    对比实验：200 / 500 / 1000 三种 chunk_size
    分别建索引、检索同一个 query、对比距离值
    """
    results = {}

    for size in [200, 500, 1000]:
        # 分块
        chunks = chunk_by_size(doc_text, chunk_size=size, overlap=50)

        # 建索引
        chroma = chromadb.Client()
        col = chroma.create_collection(name=f"exp_{size}")
        col.add(
            documents=chunks,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"source": f"chunk_size_{size}"} for _ in chunks],
        )

        # 检索
        search_result = col.query(query_texts=[query], n_results=3)
        distances = search_result["distances"][0]

        results[size] = {
            "num_chunks": len(chunks),
            "top_distance": distances[0] if distances else None,
            "avg_distance": sum(distances) / len(distances) if distances else None,
        }

    print("=== 题目 1: chunk_size 对比实验 ===")
    for size, res in results.items():
        print(f"  chunk_size={size}: {res['num_chunks']} 个块, "
              f"top距离={res['top_distance']:.4f}, "
              f"平均={res['avg_distance']:.4f}")

    best = min(results.items(), key=lambda x: x[1]["top_distance"] or float("inf"))
    print(f"  结论: chunk_size={best[0]} 检索效果最好（距离最小）")
    return results


# --- 题目 2: 相似度阈值过滤 ---

def rag_with_threshold(collection, query, client, model, n_results=3, threshold=1.5):
    """
    带阈值过滤的 RAG

    流程：
    1. 检索 n_results 条结果
    2. 过滤距离 >= threshold 的结果
    3. 如果没有通过阈值的，返回"文档中未找到相关信息"
    4. 否则拼接上下文，调 LLM 回答
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    # 过滤：L2 距离越小越相似，保留低于阈值的
    relevant = [
        (doc, meta, dist)
        for doc, meta, dist in zip(docs, metas, dists)
        if dist < threshold
    ]

    if not relevant:
        return "文档中未找到相关信息，请尝试其他问题。"

    # 拼接上下文
    context = "\n\n---\n\n".join(doc for doc, _, _ in relevant)

    prompt = f"""根据以下参考文档回答用户问题。
如果文档中没有相关信息，请说"文档中未提及"。

参考文档：
{context}

用户问题：{query}"""

    return ask(client, model, prompt, max_tokens=800)


# 测试
if __name__ == "__main__":
    # 先加载文档并建索引
    doc_dir = Path(__file__).parent.parent / "week3-rag-and-fastapi" / "sample_docs"
    all_docs = {}
    for md_file in Path(doc_dir).glob("*.md"):
        all_docs[md_file.name] = md_file.read_text(encoding="utf-8")

    chroma_test = chromadb.Client()
    col_test = chroma_test.create_collection(name="threshold_test")

    # 分块
    idx = 0
    for name, content in all_docs.items():
        paragraphs = content.split("\n\n")
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) > 500 and current:
                col_test.add(
                    documents=[current],
                    ids=[f"chunk_{idx}"],
                    metadatas=[{"source": name}],
                )
                idx += 1
                current = para
            else:
                current = current + "\n\n" + para if current else para
        if current:
            col_test.add(
                documents=[current],
                ids=[f"chunk_{idx}"],
                metadatas=[{"source": name}],
            )
            idx += 1

    client_ai, MODEL = get_client(Path(__file__).parent / ".env")

    print("\n=== 题目 2: 带阈值的 RAG ===")
    questions = ["React 的 Hooks 有哪些？", "量子计算的原理是什么？"]
    for q in questions:
        answer = rag_with_threshold(col_test, q, client_ai, MODEL, threshold=1.5)
        print(f"Q: {q}")
        print(f"A: {answer[:120]}...\n")


# --- 题目 3: 引用来源 ---

def rag_with_citations(collection, query, client, model, n_results=3):
    """
    带引用来源的 RAG

    返回: {answer, sources}
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    sources = []
    context_parts = []
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
        source = meta.get("source", "unknown")
        sources.append({
            "source": source,
            "preview": doc[:100] + "...",
            "distance": round(dist, 4),
        })
        context_parts.append(f"[来源: {source}]\n{doc}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""根据以下参考文档回答用户问题。
如果文档中没有相关信息，请说"文档中未提及"。
回答末尾请标注引用来源（文件名）。

参考文档：
{context}

用户问题：{query}"""

    answer = ask(client, model, prompt, max_tokens=800)
    return {"answer": answer, "sources": sources}


# --- 题目 4: RAG 评估 ---

# 定义评估集（至少 3 条 QA）
eval_set = [
    {
        "question": "React 有哪些常用 Hooks？",
        "expected_source": "react_basics.md",
        "expected_keywords": ["useState", "useEffect"],
    },
    {
        "question": "Python 的列表推导式怎么写？",
        "expected_source": "python_tips.md",
        "expected_keywords": ["列表", "推导"],
    },
    {
        "question": "RESTful API 设计有什么规范？",
        "expected_source": "api_design.md",
        "expected_keywords": ["REST", "资源"],
    },
]


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
        results = collection.query(
            query_texts=[item["question"]],
            n_results=n_results,
        )
        retrieved_sources = [m["source"] for m in results["metadatas"][0]]

        # 检索评估：期望来源是否在 top-k 中
        retrieval_hit = item["expected_source"] in retrieved_sources
        if retrieval_hit:
            retrieval_hits += 1

        # 生成评估：调 LLM 回答，检查关键词命中
        docs = results["documents"][0]
        context = "\n\n".join(docs)
        prompt = f"""根据以下参考文档回答用户问题。
如果文档中没有相关信息，请说"文档中未提及"。

参考文档：
{context}

用户问题：{item["question"]}"""

        answer = ask(client, model, prompt, max_tokens=500)
        matched_kws = [kw for kw in item["expected_keywords"] if kw.lower() in answer.lower()]
        # 命中一半以上算通过
        generation_hit = len(matched_kws) >= max(1, len(item["expected_keywords"]) // 2)
        if generation_hit:
            generation_hits += 1

        details.append({
            "question": item["question"],
            "retrieval_hit": retrieval_hit,
            "generation_hit": generation_hit,
            "matched_keywords": matched_kws,
            "answer_preview": answer[:80] + "...",
        })

    total = len(eval_set)
    return {
        "retrieval_hit_rate": retrieval_hits / total,
        "generation_pass_rate": generation_hits / total,
        "details": details,
    }


# 测试评估
if __name__ == "__main__":
    # 建索引
    col_eval = chromadb.Client().create_collection(name="eval_test")
    idx = 0
    for name, content in all_docs.items():
        paragraphs = content.split("\n\n")
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) > 500 and current:
                col_eval.add(
                    documents=[current],
                    ids=[f"e_{idx}"],
                    metadatas=[{"source": name}],
                )
                idx += 1
                current = para
            else:
                current = current + "\n\n" + para if current else para
        if current:
            col_eval.add(
                documents=[current],
                ids=[f"e_{idx}"],
                metadatas=[{"source": name}],
            )
            idx += 1

    print("\n=== 题目 4: RAG 评估 ===")
    result = run_eval(col_eval, client_ai, MODEL, eval_set)
    print(f"检索命中率: {result['retrieval_hit_rate']:.0%}")
    print(f"生成通过率: {result['generation_pass_rate']:.0%}")
    for d in result["details"]:
        print(f"  {d['question']}: "
              f"检索={'✅' if d['retrieval_hit'] else '❌'}, "
              f"生成={'✅' if d['generation_hit'] else '❌'}")


# --- 题目 5: 思考题 ---

# 场景 1：用户问了一个完全无关的问题，AI 基于不相关内容编造了答案
# 方案：设置相似度阈值，低于阈值拒绝回答；在 prompt 中强调"如果文档中没有相关信息就说不知道"
#
# 场景 2：检索结果总是包含不相关的文档，回答质量差
# 方案：减小 top_k（只取最相关的几条）、调整 chunk_size（让每个块更聚焦）、引入 Rerank 二次排序
#
# 场景 3：回答总是很简短，漏掉重要信息
# 方案：增加 top_k（提供更多上下文）、优化 prompt 模板（要求"详细回答"）、增大 max_tokens
