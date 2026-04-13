# ===========================================
# Day 3: RAG 优化 — 从"能用"到"好用"
# ===========================================
# Day 1 我们搭了一个能跑的 RAG，但效果一般
# 今天学怎么调优，让检索更准、回答更好
#
# 前端类比：
# Day 1 的 RAG = 写了个能跑的页面（但没做性能优化）
# 今天 = 做 Lighthouse 优化、做 SEO、做缓存策略
#
# RAG 调优的核心维度：
# 1. chunk_size — 文档切多大？
# 2. top_k — 检索几条结果？
# 3. threshold — 相似度多高才算"相关"？
# 4. rerank — 检索结果要不要重新排序？
# 5. 评估 — 怎么知道优化有没有效果？
# ===========================================

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

import chromadb


# ===========================================
# 1. Chunk 大小实验 — 切多大最合适？
# ===========================================
# 分块大小是 RAG 效果的第一个关键因素
#
# 块太大 → 噪音多，检索不精准，浪费 token
# 块太小 → 丢失上下文，语义不完整
#
# JS 类比：
# 想象你做搜索功能，索引粒度的选择：
# - 按整篇文章索引 → 搜到了但不知道哪段有用（块太大）
# - 按每个单词索引 → 搜到了但看不懂上下文（块太小）
# - 按段落索引 → 刚刚好（合适的块大小）
#
# 常见范围：200-1000 字符
# 我们用 200 / 500 / 1000 三种大小做对比实验

print("=== 1. Chunk 大小实验 ===\n")

# --- 辅助函数：按固定大小分块 ---
def chunk_by_size(text, chunk_size=300, overlap=50):
    """
    按固定字数分块，带重叠

    JS 类比：
    function chunkBySize(text, size, overlap) {
        const chunks = [];
        for (let i = 0; i < text.length; i += size - overlap) {
            chunks.push(text.slice(i, i + size));
        }
        return chunks;
    }
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# --- 读取所有示例文档 ---
doc_dir = Path(__file__).parent / "sample_docs"
all_text = ""
doc_sources = {}  # 记录每段文本来自哪个文件

for doc_path in doc_dir.glob("*.md"):
    text = doc_path.read_text(encoding="utf-8")
    all_text += text + "\n\n"

# --- 用三种大小建索引，对比检索结果 ---
chroma_client = chromadb.Client()
query = "React 的常用 Hooks 有哪些？"
chunk_sizes = [200, 500, 1000]

for size in chunk_sizes:
    # 分块
    chunks = chunk_by_size(all_text, chunk_size=size, overlap=50)

    # 创建 collection（每种大小一个）
    collection_name = f"chunk_{size}"
    collection = chroma_client.get_or_create_collection(name=collection_name)
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )

    # 检索
    results = collection.query(query_texts=[query], n_results=2)

    print(f"--- chunk_size = {size} 字符 ---")
    print(f"总块数: {len(chunks)}")
    for i, (doc, dist) in enumerate(zip(
        results["documents"][0], results["distances"][0]
    )):
        # 截取前 80 字符展示
        preview = doc[:80].replace("\n", " ")
        print(f"  结果 {i+1} [距离={dist:.4f}]: {preview}...")
    print()

print("观察：")
print("  - 200 字符：块多、精确但可能丢失上下文")
print("  - 500 字符：通常是最佳平衡点")
print("  - 1000 字符：块少、上下文完整但噪音多\n")


# ===========================================
# 2. top-k 调整 — 检索几条最合适？
# ===========================================
# top_k = 返回最相似的 k 条结果
#
# k 太小 → 可能漏掉重要信息
# k 太大 → 塞太多内容进 prompt，噪音多 + 浪费 token
#
# JS 类比：
# 搜索结果分页：
# - 只看第 1 条 → 可能错过更好的答案
# - 看 100 条  → 信息过载，根本看不完
# - 看 3-5 条  → 刚刚好
#
# 一般建议：3-5 条，根据文档数量调整

# print("\n=== 2. top-k 调整 ===\n")
#
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
#
# # 用 500 字符的分块做实验
# collection_500 = chroma_client.get_or_create_collection(name="chunk_500")
# query = "React 的常用 Hooks 有哪些？"
#
# for k in [1, 3, 5]:
#     results = collection_500.query(query_texts=[query], n_results=k)
#     context = "\n\n---\n\n".join(results["documents"][0])
#
#     # 用 LLM 基于检索结果回答
#     rag_prompt = f"""根据以下参考文档回答用户问题。只使用文档中的信息，不要编造。
#
# 参考文档：
# {context}
#
# 用户问题：{query}"""
#
#     answer = ask(client_ai, MODEL, rag_prompt, max_tokens=300)
#
#     print(f"--- top_k = {k} ---")
#     print(f"检索到 {len(results['documents'][0])} 个片段")
#     print(f"上下文总长度: {len(context)} 字符")
#     print(f"AI 回答: {answer[:150]}...")
#     print()
#
# print("观察：")
# print("  - k=1：回答可能不完整，只基于一个片段")
# print("  - k=3：通常最佳，信息充分且噪音少")
# print("  - k=5：信息最多，但可能引入不相关内容\n")


# ===========================================
# 3. 引用来源展示 — 让回答有据可查
# ===========================================
# RAG 最大的优势之一：回答可以追溯到原始文档
# 用户不仅看到答案，还能看到"AI 是根据哪段话回答的"
#
# JS 类比：
# 就像搜索引擎的结果页：
# - 标题（AI 的回答）
# - 来源链接（原始文档 + 文件名）
# - 摘要（原文片段）
#
# 实现方式：在 metadata 中存文件名，检索时一起返回

# print("\n=== 3. 引用来源展示 ===\n")
#
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
# chroma_src = chromadb.Client()
#
# # --- 建索引时存入来源信息 ---
# src_collection = chroma_src.create_collection(name="with_source")
#
# all_chunks = []
# all_ids = []
# all_metadatas = []
#
# for doc_path in doc_dir.glob("*.md"):
#     text = doc_path.read_text(encoding="utf-8")
#     chunks = chunk_by_size(text, chunk_size=500, overlap=50)
#     for i, chunk in enumerate(chunks):
#         all_chunks.append(chunk)
#         all_ids.append(f"{doc_path.stem}_{i}")
#         all_metadatas.append({
#             "source": doc_path.name,          # 来源文件名
#             "chunk_index": i,                   # 第几块
#         })
#
# src_collection.add(
#     documents=all_chunks,
#     ids=all_ids,
#     metadatas=all_metadatas,
# )
#
# # --- 检索并展示来源 ---
# query = "Python 的异步编程怎么用？"
# results = src_collection.query(query_texts=[query], n_results=3)
#
# print(f"问题: {query}\n")
#
# # 构造带来源的上下文
# context_parts = []
# print("📎 检索到的参考来源：")
# for i, (doc, meta, dist) in enumerate(zip(
#     results["documents"][0],
#     results["metadatas"][0],
#     results["distances"][0],
# )):
#     print(f"  [{i+1}] 来源: {meta['source']} (第 {meta['chunk_index']+1} 块)")
#     print(f"      距离: {dist:.4f}")
#     print(f"      内容: {doc[:80].replace(chr(10), ' ')}...")
#     print()
#     context_parts.append(f"[来源: {meta['source']}]\n{doc}")
#
# # --- 让 AI 带引用回答 ---
# context = "\n\n---\n\n".join(context_parts)
# rag_prompt = f"""根据以下参考文档回答用户问题。
# 要求：
# 1. 只使用文档中的信息
# 2. 回答末尾标注引用来源（文件名）
#
# 参考文档：
# {context}
#
# 用户问题：{query}"""
#
# answer = ask(client_ai, MODEL, rag_prompt, max_tokens=500)
# print(f"AI 回答：\n{answer}\n")


# ===========================================
# 4. 相似度阈值 — 过滤不相关结果
# ===========================================
# 问题：如果用户问了一个文档里完全没有的问题，
# 向量库还是会返回"最相似"的结果（只是没那么相似）
# AI 可能基于不相关内容瞎答
#
# 解决：设定距离阈值，超过阈值 → 认为不相关 → 拒绝回答
#
# JS 类比：
# 就像表单验证 — 不是什么输入都接受：
# if (similarity < threshold) {
#   return "没有找到相关信息";
# }
#
# Chroma 用 L2 距离（越小越相似）：
# - < 0.5 : 非常相关
# - 0.5 ~ 1.0 : 一般相关
# - > 1.5 : 基本不相关（阈值因模型而异，需要实验）

# print("\n=== 4. 相似度阈值 ===\n")
#
# # 复用第 3 节的 collection
# # 测试不同问题的距离
# test_queries = [
#     "React 的 Hooks 有哪些？",      # 文档中有 → 距离应该小
#     "Python 异步编程怎么用？",        # 文档中有 → 距离应该小
#     "量子计算的原理是什么？",          # 文档中没有 → 距离应该大
#     "怎么炒宫保鸡丁？",              # 完全无关 → 距离应该很大
# ]
#
# DISTANCE_THRESHOLD = 1.5  # 距离阈值，需要根据实际情况调整
#
# for q in test_queries:
#     results = src_collection.query(query_texts=[q], n_results=1)
#     distance = results["distances"][0][0]
#     doc = results["documents"][0][0]
#     source = results["metadatas"][0][0]["source"]
#
#     # 判断是否通过阈值
#     is_relevant = distance < DISTANCE_THRESHOLD
#
#     print(f"问题: {q}")
#     print(f"  最近距离: {distance:.4f}")
#     print(f"  最近来源: {source}")
#     if is_relevant:
#         print(f"  ✅ 通过阈值 (< {DISTANCE_THRESHOLD})，可以回答")
#     else:
#         print(f"  ❌ 未通过阈值 (>= {DISTANCE_THRESHOLD})，拒绝回答")
#         print(f"  → 回复: '文档中未找到相关信息'")
#     print()
#
# # --- 封装成可复用的 RAG 函数 ---
# def rag_with_threshold(collection, query, client, model,
#                        n_results=3, threshold=1.5):
#     """
#     带阈值过滤的 RAG
#
#     JS 类比：
#     async function ragQuery(query, { nResults, threshold }) {
#       const results = await search(query, nResults);
#       const relevant = results.filter(r => r.distance < threshold);
#       if (relevant.length === 0) return "文档中未找到相关信息";
#       return await askAI(relevant, query);
#     }
#     """
#     results = collection.query(query_texts=[query], n_results=n_results)
#
#     # 过滤：只保留距离小于阈值的结果
#     filtered_docs = []
#     filtered_metas = []
#     for doc, meta, dist in zip(
#         results["documents"][0],
#         results["metadatas"][0],
#         results["distances"][0],
#     ):
#         if dist < threshold:
#             filtered_docs.append(doc)
#             filtered_metas.append(meta)
#
#     # 如果没有相关结果，直接拒绝
#     if not filtered_docs:
#         return "文档中未找到相关信息，无法回答该问题。"
#
#     # 拼接上下文
#     context = "\n\n---\n\n".join(
#         f"[来源: {m['source']}]\n{d}"
#         for d, m in zip(filtered_docs, filtered_metas)
#     )
#
#     rag_prompt = f"""根据以下参考文档回答用户问题。
# 只使用文档中的信息，不要编造。回答末尾标注引用来源。
#
# 参考文档：
# {context}
#
# 用户问题：{query}"""
#
#     return ask(client, model, rag_prompt, max_tokens=500)
#
#
# # 测试带阈值的 RAG
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
#
# print("--- 带阈值的 RAG 测试 ---\n")
# for q in ["React 的性能优化方法？", "怎么炒宫保鸡丁？"]:
#     answer = rag_with_threshold(src_collection, q, client_ai, MODEL)
#     print(f"问题: {q}")
#     print(f"回答: {answer[:200]}")
#     print()


# ===========================================
# 5. Rerank 概念介绍 — 对检索结果重新排序
# ===========================================
# 向量检索只是粗排（recall），不一定精准
# Rerank 是在检索之后，用更精确的模型重新打分排序
#
# 类比理解（非常重要！）：
#
# Bi-encoder（双编码器）= 当前我们用的方式
#   - 文档和查询分别独立编码成向量
#   - 然后算距离
#   - 速度快，但精度一般
#   - 类比：简历关键词匹配 — 快速筛出候选人
#
# Cross-encoder（交叉编码器）= Rerank 模型
#   - 把文档和查询一起输入模型，直接输出相关性分数
#   - 速度慢（因为要一对一比较），但精度高
#   - 类比：面试 — 深入评估每个候选人
#
# 完整流程：
#   1. Bi-encoder 检索 top-20（快速召回）
#   2. Cross-encoder 对这 20 条重新打分（精准排序）
#   3. 取 top-3 送给 LLM
#
# JS 类比：
# // 两阶段搜索，类似前端的 debounce + 详细搜索
# const candidates = quickSearch(query, { limit: 20 });   // Bi-encoder: 快速粗筛
# const reranked = detailedScore(query, candidates);       // Cross-encoder: 精排
# const topResults = reranked.slice(0, 3);                 // 取最终结果
#
# 常用 Rerank 方案：
# 1. Cohere Rerank API — 商业方案，效果好
# 2. sentence-transformers CrossEncoder — 开源方案
# 3. bge-reranker — 中文效果好的开源模型
#
# 注意：本节只介绍概念，不实际实现
# 因为 Rerank 模型需要额外安装和下载，我们重点理解思路

# print("\n=== 5. Rerank 概念介绍 ===\n")
#
# print("Bi-encoder vs Cross-encoder：")
# print()
# print("  Bi-encoder（当前方案）:")
# print("    查询 → [向量]  ←比较距离→  [向量] ← 文档")
# print("    特点：快（可以预计算文档向量），精度一般")
# print()
# print("  Cross-encoder（Rerank）:")
# print("    [查询 + 文档] → 一起输入模型 → 相关性分数")
# print("    特点：慢（每对都要重新计算），精度高")
# print()
# print("  实际使用：先 Bi-encoder 召回 20 条，再 Cross-encoder 精排取 3 条")
# print()
# print("  伪代码：")
# print("  # Step 1: 粗排（Bi-encoder，我们已经会了）")
# print("  candidates = collection.query(query, n_results=20)")
# print()
# print("  # Step 2: 精排（Cross-encoder）")
# print("  # from sentence_transformers import CrossEncoder")
# print("  # reranker = CrossEncoder('BAAI/bge-reranker-base')")
# print("  # pairs = [[query, doc] for doc in candidates]")
# print("  # scores = reranker.predict(pairs)")
# print("  # top3 = sorted(zip(scores, candidates), reverse=True)[:3]")
# print()
# print("  什么时候需要 Rerank？")
# print("  - 文档量大（> 1000 条）且检索精度不够时")
# print("  - 简单项目不需要，先把 chunk_size 和 top_k 调好\n")


# ===========================================
# 6. 评估 RAG — 怎么知道 RAG 效果好不好？
# ===========================================
# 最重要的一节！很多人做 RAG 全凭感觉调参数
# 正确做法：建评估集，用数据说话
#
# RAG 评估分两部分（非常关键的概念！）：
#
# 1. 检索评估（Retrieval Evaluation）
#    - 问题：检索到的文档块是否正确？
#    - 指标：命中率（Hit Rate）、MRR
#    - 类比：搜索引擎有没有把对的结果排在前面
#
# 2. 生成评估（Generation Evaluation）
#    - 问题：AI 基于检索结果的回答是否正确？
#    - 指标：准确率、完整率
#    - 类比：AI 看了对的文档，有没有正确理解并回答
#
# 分开评估的好处：
# - 如果检索对了但回答错了 → 优化 prompt
# - 如果检索错了 → 优化 chunk_size / embedding / rerank
# - 如果都对了但用户不满意 → 优化回答格式
#
# JS 类比：
# 单元测试 vs 集成测试：
# - 检索评估 = 单元测试（搜索功能本身对不对？）
# - 生成评估 = 集成测试（整个流程跑通，最终结果对不对？）

# print("\n=== 6. 评估 RAG ===\n")
#
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
# chroma_eval = chromadb.Client()
#
# # --- Step 1: 建索引（复用前面的逻辑）---
# eval_collection = chroma_eval.create_collection(name="eval_rag")
#
# all_chunks = []
# all_ids = []
# all_metadatas = []
#
# for doc_path in doc_dir.glob("*.md"):
#     text = doc_path.read_text(encoding="utf-8")
#     chunks = chunk_by_size(text, chunk_size=500, overlap=50)
#     for i, chunk in enumerate(chunks):
#         all_chunks.append(chunk)
#         all_ids.append(f"{doc_path.stem}_{i}")
#         all_metadatas.append({"source": doc_path.name})
#
# eval_collection.add(
#     documents=all_chunks,
#     ids=all_ids,
#     metadatas=all_metadatas,
# )
#
# # --- Step 2: 定义评估集（3 组 QA 对）---
# # 每组包含：问题、期望来源文件、期望答案关键词
# eval_set = [
#     {
#         "question": "React 的常用 Hooks 有哪些？",
#         "expected_source": "react_basics.md",
#         "expected_keywords": ["useState", "useEffect", "useContext"],
#     },
#     {
#         "question": "RESTful API 的 HTTP 方法有哪些？",
#         "expected_source": "api_design.md",
#         "expected_keywords": ["GET", "POST", "PUT", "DELETE"],
#     },
#     {
#         "question": "Python 的列表推导式怎么用？",
#         "expected_source": "python_tips.md",
#         "expected_keywords": ["列表推导", "filter", "map"],
#     },
# ]
#
# # --- Step 3: 运行评估 ---
# print("检索评估 + 生成评估\n")
# print("=" * 60)
#
# retrieval_hits = 0  # 检索命中数
# generation_hits = 0  # 生成命中数
#
# for i, item in enumerate(eval_set):
#     q = item["question"]
#     expected_src = item["expected_source"]
#     expected_kws = item["expected_keywords"]
#
#     # 检索
#     results = eval_collection.query(query_texts=[q], n_results=3)
#     retrieved_sources = [
#         m["source"] for m in results["metadatas"][0]
#     ]
#
#     # 检索评估：期望来源是否在 top-3 中？
#     retrieval_hit = expected_src in retrieved_sources
#     if retrieval_hit:
#         retrieval_hits += 1
#
#     # 生成评估：AI 回答中是否包含期望关键词？
#     context = "\n\n---\n\n".join(results["documents"][0])
#     rag_prompt = f"""根据以下参考文档回答用户问题。只使用文档中的信息。
#
# 参考文档：
# {context}
#
# 用户问题：{q}"""
#
#     answer = ask(client_ai, MODEL, rag_prompt, max_tokens=300)
#
#     # 检查关键词命中
#     kw_hits = [kw for kw in expected_kws if kw in answer]
#     generation_hit = len(kw_hits) >= len(expected_kws) // 2 + 1
#     if generation_hit:
#         generation_hits += 1
#
#     # 打印结果
#     print(f"\n--- 评估 {i+1}: {q} ---")
#     print(f"  检索来源: {retrieved_sources}")
#     print(f"  期望来源: {expected_src}")
#     print(f"  检索评估: {'✅ 命中' if retrieval_hit else '❌ 未命中'}")
#     print(f"  AI 回答: {answer[:120]}...")
#     print(f"  关键词命中: {kw_hits} / {expected_kws}")
#     print(f"  生成评估: {'✅ 通过' if generation_hit else '❌ 未通过'}")
#
# # --- Step 4: 汇总 ---
# total = len(eval_set)
# print(f"\n{'=' * 60}")
# print(f"评估汇总 ({total} 组测试):")
# print(f"  检索命中率: {retrieval_hits}/{total} ({retrieval_hits/total:.0%})")
# print(f"  生成通过率: {generation_hits}/{total} ({generation_hits/total:.0%})")
# print()
# print("如何根据结果优化：")
# print("  - 检索命中率低 → 调整 chunk_size、换 embedding 模型、加 rerank")
# print("  - 生成通过率低 → 优化 prompt 模板、增加上下文、调整 top_k")
# print("  - 两个都低 → 检查文档质量，可能需要更好的文档\n")
