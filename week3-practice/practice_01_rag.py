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

# TODO 1.1: 用你自己的话解释 RAG 是什么？（类比：开卷考试 vs 闭卷考试）
# 提示：RAG = Retrieval-Augmented Generation（检索增强生成）
#
# 你的理解：
# RAG 的工作流程是：
# 1. 离线阶段：文档 → ___ → ___ → 存入向量库
# 2. 在线阶段：用户提问 → ___ → ___ → 取 top-k → 拼接 prompt → ___


# --- 题目 2: Chunking（分块）---

# TODO 2.1: 手写一个按固定大小分块的函数
def chunk_by_size(text, chunk_size=300, overlap=50):
    """
    按固定字数分块，带重叠
    """
    # TODO: 实现分块逻辑
    chunks = []
    start = 0
    while start < len(text):
        # 你的代码
        pass
    return chunks


# 测试
test_text = "这是第1句。这是第2句。这是第3句。这是第4句。这是第5句。这是第6句。"
# TODO 2.2: 调用 chunk_by_size(test_text, chunk_size=20, overlap=5)
# 预期：多块，每块约 20 字符，相邻块有 5 字符重叠


# TODO 2.3: 手写一个按段落分块的函数
def chunk_by_paragraph(text):
    """按段落分块，过滤空段落和太短的段落（< 10 字符）"""
    # TODO: 用 split("\n\n") 分块，strip 后过滤
    pass


# --- 题目 3: Embedding 概念 ---

# TODO 3.1: 选择题（写出答案）
# 以下关于 Embedding 的说法，哪些是正确的？
# A. Embedding 把文本转成一组数字（向量）
# B. 语义相近的文本，向量也相近
# C. Embedding 必须在云端调 API 完成
# D. Chroma 默认的 embedding 模型是免费的本地模型
#
# 你的答案：___


# TODO 3.2: 填空题
# Chroma 的 collection.add() 会自动做 ___（向量化）
# collection.query() 会自动把查询文本 ___ 然后找最 ___ 的结果
# 距离越 ___ 表示越相似（L2 距离）


# --- 题目 4: 相似度计算 ---

# TODO 4.1: 手写余弦相似度计算函数
def cosine_similarity(v1, v2):
    """
    计算两个向量的余弦相似度

    公式：cos(a,b) = (a·b) / (|a| * |b|)
    其中 a·b 是点积，|a| 是向量的模（L2 范数）

    JS 类比：
    function cosineSim(v1, v2) {
        const dot = v1.reduce((sum, a, i) => sum + a * v2[i], 0);
        const norm1 = Math.sqrt(v1.reduce((sum, a) => sum + a*a, 0));
        const norm2 = Math.sqrt(v2.reduce((sum, a) => sum + a*a, 0));
        return dot / (norm1 * norm2);
    }
    """
    import math
    # TODO: 计算点积、两个向量的模、返回余弦相似度
    # 提示：点积 = sum(a*b for a,b in zip(v1,v2))
    #       模 = sqrt(sum(a*a for a in v))
    pass


# 测试
# v1 = [0.1, 0.2, 0.3]
# v2 = [0.1, 0.2, 0.3]  # 相同向量 → 应该返回 1.0
# v3 = [1.0, 0.0, 0.0]  # 正交向量 → 应该接近 0
# print(cosine_similarity(v1, v2))  # 预期: 1.0
# print(cosine_similarity(v1, v3))  # 预期: ~0.267


# --- 题目 5: 综合思考 ---

# TODO 5.1: 设计题
# 你有一个 10 万字的内部技术文档库，要搭建一个 RAG 问答系统。
# 请回答：
# 1. 你会选多大的 chunk_size？为什么？
# 2. top_k 设多少？为什么？
# 3. 需要设置相似度阈值吗？阈值设多少？
# 4. 如何评估这个 RAG 系统的效果？
#
# 你的设计：
# 1. chunk_size = ___，因为：___
# 2. top_k = ___，因为：___
# 3. 阈值：___，因为：___
# 4. 评估方法：___
