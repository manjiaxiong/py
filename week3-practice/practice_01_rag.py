# ===========================================
# 练习 1：RAG 基础概念（对应 Day 1）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 01_rag_basics.py / 01_rag_basics.md
# ===========================================

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


# --- 题目 1: RAG 概念 ---

# RAG = Retrieval-Augmented Generation（检索增强生成）
# 类比：开卷考试 —— AI 不靠死记硬背，而是先查资料再回答
#
# RAG 的工作流程是：
# 1. 离线阶段：文档 → 分块(chunking) → 向量化(embedding) → 存入向量库
# 2. 在线阶段：用户提问 → 向量化(embedding) → 相似度检索 → 取 top-k → 拼接 prompt → LLM 生成回答


# --- 题目 2: Chunking（分块）---

# 按固定大小分块，带重叠
def chunk_by_size(text, chunk_size=300, overlap=50):
    """
    按固定字数分块，带重叠
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# 测试
test_text = "这是第1句。这是第2句。这是第3句。这是第4句。这是第5句。这是第6句。"
result = chunk_by_size(test_text, chunk_size=20, overlap=5)
print("=== 题目 2.1: 按固定大小分块 ===")
for i, chunk in enumerate(result):
    print(f"  块 {i}: [{chunk}] ({len(chunk)} 字符)")


# 按段落分块
def chunk_by_paragraph(text):
    """按段落分块，过滤空段落和太短的段落（< 10 字符）"""
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if len(p.strip()) >= 10]


# 测试
test_paragraphs = """这是第一段，包含足够多的文字来测试分段功能。

太短

这是第三段，也包含足够多的文字，应该被保留下来。

xy

最后一段，同样有足够的内容可以通过长度过滤。"""

print("\n=== 题目 2.3: 按段落分块 ===")
paragraphs = chunk_by_paragraph(test_paragraphs)
for i, p in enumerate(paragraphs):
    print(f"  段 {i}: [{p}]")


# --- 题目 3: Embedding 概念 ---

# 选择题答案：A B D
# A. ✅ Embedding 把文本转成一组数字（向量）
# B. ✅ 语义相近的文本，向量也相近
# C. ❌ Embedding 不一定要云端 API，可以用本地模型（如 Chroma 默认的 all-MiniLM-L6-v2）
# D. ✅ Chroma 默认的 embedding 模型是免费的本地模型

# 填空题答案：
# Chroma 的 collection.add() 会自动做 embedding（向量化）
# collection.query() 会自动把查询文本 向量化 然后找最 近（距离最小） 的结果
# 距离越 小 表示越相似（L2 距离）


# --- 题目 4: 相似度计算 ---

def cosine_similarity(v1, v2):
    """
    计算两个向量的余弦相似度

    公式：cos(a,b) = (a·b) / (|a| * |b|)
    其中 a·b 是点积，|a| 是向量的模（L2 范数）
    """
    import math
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(a * a for a in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


# 测试
v1 = [0.1, 0.2, 0.3]
v2 = [0.1, 0.2, 0.3]  # 相同向量 → 应该返回 1.0
v3 = [1.0, 0.0, 0.0]  # 正交向量 → 应该接近 0

print("\n=== 题目 4: 余弦相似度 ===")
print(f"  相同向量: {cosine_similarity(v1, v2):.4f}")   # 预期: 1.0
print(f"  正交向量: {cosine_similarity(v1, v3):.4f}")   # 预期: ~0.2673


# --- 题目 5: 综合思考 ---

# 设计题答案：
# 1. chunk_size = 500，因为：技术文档段落通常 300-800 字，500 是平衡点。
#    太小（200）会切断上下文，太大（1000）会引入噪音。
# 2. top_k = 3，因为：3 条既能提供足够上下文，又不会让 prompt 太长。
#    可以从 3 开始，根据评估结果调到 5。
# 3. 阈值：L2 距离 1.5 左右，因为：超过这个距离说明检索结果不太相关，
#    应该拒绝回答，避免 AI 基于不相关内容编造答案。
# 4. 评估方法：
#    - 检索评估：准备 QA 测试集，检查期望文档是否在 top-k 中（检索命中率）
#    - 生成评估：检查回答是否包含期望关键词（关键词命中率）
#    - 拒答评估：无关问题是否正确拒绝回答
