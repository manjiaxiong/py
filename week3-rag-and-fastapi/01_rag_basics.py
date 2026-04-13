# ===========================================
# Day 1: RAG 基础概念 — 让 AI 查资料再回答
# ===========================================
# RAG = Retrieval-Augmented Generation（检索增强生成）
# 一句话：AI 不靠记忆回答，而是先查资料再回答
#
# 类比：
# 不用 RAG = 闭卷考试（AI 只靠训练时的记忆）
# 用 RAG   = 开卷考试（AI 先翻书找答案，再组织语言回答）
#
# 前端类比：
# RAG = 带搜索框的页面，用户问问题 → 搜索 → 展示结果
# ===========================================

# 安装（如果还没装）：
# pip install chromadb

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask


# ===========================================
# 1. 什么是 RAG？
# ===========================================
# AI 大模型有两个致命问题：
# 1. 知识截止 — 训练数据有截止日期，不知道最新信息
# 2. 不知道私有数据 — 你的公司文档、个人笔记它都不知道
#
# RAG 的解决方案：
# 用户提问 → 从你的文档库中检索相关内容 → 把检索结果塞进 prompt → AI 基于这些内容回答
#
# JS 类比：
# 没有 RAG: ChatGPT("React 18 有什么新特性？") → 可能过时或编造
# 有 RAG:   search("React 18") → 找到文档片段 → ChatGPT("根据以下文档回答: ...") → 准确回答

print("=== 1. RAG 概念 ===\n")
print("RAG = 检索增强生成")
print("流程: 用户提问 → 检索文档 → 拼接 prompt → AI 回答")
print("解决: AI 知识截止 + 不知道私有数据\n")


# ===========================================
# 2. 为什么需要 RAG？
# ===========================================
# 对比三种方案：
#
# | 方案 | 优点 | 缺点 |
# |------|------|------|
# | 直接问 AI | 简单 | 可能过时/编造 |
# | 微调模型 | 效果好 | 贵、慢、需要大量数据 |
# | RAG | 便宜、实时、可控 | 检索质量影响回答质量 |
#
# RAG 是性价比最高的方案，几乎所有 AI 应用都在用

# print("\n=== 2. 为什么需要 RAG ===\n")

client, MODEL = get_client(Path(__file__).parent / ".env")

# 不用 RAG — AI 可能编造或过时
# result_no_rag = ask(client, MODEL, "Python 的 Pydantic v2 有什么重大变化？")
# print(f"不用 RAG: {result_no_rag[:200]}...\n")

# # 用 RAG — 先提供文档内容
# doc_content = "Pydantic v2 用 Rust 重写了核心，性能提升 5-50 倍。model_dump() 替代了 .dict()，model_validate() 替代了 parse_obj()。"
# result_with_rag = ask(client, MODEL,
#     f"根据以下文档回答问题。如果文档中没有相关信息，说'文档中未提及'。\n\n文档：{doc_content}\n\n问题：Pydantic v2 有什么变化？"
# )
# print(f"用 RAG: {result_with_rag[:200]}...\n")


# ===========================================
# 3. Chunking — 文档分块
# ===========================================
# 为什么要分块？
# - 文档太长，塞不进 prompt（token 限制）
# - 整篇文档噪音太多，检索不精准
# - 小块更容易匹配到精确答案
#
# 分块策略：
# 1. 按固定字数切 — 简单粗暴，可能切断句子
# 2. 按段落切 — 保留语义完整性
# 3. 递归切分 — 先按段落，太长再按句子，再按字数
#
# JS 类比：
# chunking = str.match(/.{1,500}/g)  但要更聪明地切

print("\n=== 3. Chunking（文档分块）===\n")

# 读取示例文档
doc_path = Path(__file__).parent / "sample_docs" / "react_basics.md"
full_text = doc_path.read_text(encoding="utf-8")
print(f"原始文档长度: {len(full_text)} 字符\n")

# --- 方法 1: 按固定字数切 ---
def chunk_by_size(text, chunk_size=300, overlap=50):
    """
    按固定字数分块

    参数:
        text: 原始文本
        chunk_size: 每块大小
        overlap: 相邻块的重叠字数（防止切断关键信息）

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
        start = end - overlap  # 重叠，防止切断
    return chunks

chunks_fixed = chunk_by_size(full_text, chunk_size=300, overlap=50)
print(f"方法 1（固定字数）: {len(chunks_fixed)} 块")
# print(f"chunks_fixed[:3]: {chunks_fixed[0]}")
# for i, chunk in enumerate(chunks_fixed[:3]):
#     print(f"pppppppppppppppppp  块 {i}: {chunk[:60]}...")

# --- 方法 2: 按段落切 ---
def chunk_by_paragraph(text):
    """
    按段落分块 — 用双换行符切分

    优点: 保留语义完整性
    缺点: 段落太长怎么办？
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs

chunks_para = chunk_by_paragraph(full_text)
# print(f"\n方法 2（按段落）: {len(chunks_para)} 块")
# for i, chunk in enumerate(chunks_para[:3]):
#     print(f"  块 {i}: {chunk[:60]}...")


# ===========================================
# 4. Embedding — 文本向量化
# ===========================================
# 问题：怎么找到"和用户问题最相关"的文档块？
# 答案：把文本变成数字向量，算向量之间的距离
#
# Embedding = 把文本转成一组数字（向量）
# 语义相近的文本，向量也相近
#
# 例子:
# "React 组件" → [0.12, 0.85, -0.33, ...]  (384维)
# "Vue 组件"   → [0.15, 0.82, -0.30, ...]  (很接近！)
# "Python 列表" → [0.78, -0.12, 0.45, ...]  (很远)
#
# JS 类比：
# Embedding 就像给每段文本生成一个"指纹"
# 搜索 = 比较指纹的相似度

print("\n=== 4. Embedding（文本向量化）===\n")
#
import chromadb

# Chroma 自带默认 embedding 模型（all-MiniLM-L6-v2）
# 第一次运行会自动下载（约 80MB），之后本地缓存
# 不需要调 API，不花钱！
chroma_client = chromadb.Client()

# 创建一个 collection（= 数据库的 table）
collection = chroma_client.create_collection(name="demo")

# 添加文档（Chroma 自动做 embedding）
texts = [
    "React 是 Facebook 开发的 UI 库，核心思想是组件化",
    "Vue 是尤雨溪开发的渐进式框架，上手简单",
    "Python 的列表推导式可以一行搞定 filter + map",
    "FastAPI 是 Python 最快的 Web 框架，类似 Express",
    "Docker 容器化技术让部署变得简单可复现",
]

collection.add(
    documents=texts,
    ids=[f"doc_{i}" for i in range(len(texts))],
)
print(f"已添加 {len(texts)} 条文档到向量库\n")

# 查询 — Chroma 自动把查询文本 embedding，然后找最相似的
results = collection.query(
    query_texts=["前端框架"],
    n_results=3,  # 返回最相似的 3 条
)
# print(results)  # 包含 "documents" 和 "distances" 两个字段
# print("查询: '前端框架'")
# print(f"结果（top-3）:")
# for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0])):
#     print(f"  {i+1}. [{dist:.4f}] {doc}")
# print(f"\n距离越小 = 越相似（0 = 完全一样）")


# ===========================================
# 5. 相似度检索
# ===========================================
# Chroma 默认用 L2 距离（欧氏距离）
# 也可以用余弦相似度（cosine similarity）
#
# 余弦相似度：
# - 1 = 完全相同方向
# - 0 = 完全无关
# - -1 = 完全相反
#
# JS 类比：
# 就像全文搜索（Elasticsearch）但是基于语义而不是关键词
# "React 组件" 能搜到 "Vue 组件"（语义相近）
# 传统搜索只能搜到包含"React"的文档

print("\n=== 5. 相似度检索 ===\n")

# 用余弦相似度创建 collection
collection_cos = chroma_client.create_collection(
    name="demo_cosine",
    metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
)

collection_cos.add(
    documents=texts,
    ids=[f"doc_{i}" for i in range(len(texts))],
)

# 多个查询测试
# queries = ["前端框架", "后端开发", "容器部署"]
# for q in queries:
#     results = collection_cos.query(query_texts=[q], n_results=2)
#     print(f"查询: '{q}'")
#     for doc, dist in zip(results["documents"][0], results["distances"][0]):
#         similarity = 1 - dist  # 余弦距离转相似度
#         print(f"  [{similarity:.2%}] {doc[:50]}...")
#     print()


# ===========================================
# 6. 完整 RAG 流程演示
# ===========================================
# 把前面所有步骤串起来：
# 1. 读文档 → 分块
# 2. 存入向量库（自动 embedding）
# 3. 用户提问 → 检索相关块
# 4. 拼接 prompt → 调 LLM 生成回答

print("\n=== 6. 完整 RAG 流程 ===\n")

import chromadb

client_ai, MODEL = get_client(Path(__file__).parent / ".env")
chroma = chromadb.Client()

# --- Step 1: 读文档 + 分块 ---
doc_dir = Path(__file__).parent / "sample_docs"
all_chunks = []
all_ids = []
all_metadata = []

for doc_path in doc_dir.glob("*.md"):
    text = doc_path.read_text(encoding="utf-8")
    # 按段落分块
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and len(p.strip()) > 20]
    for i, para in enumerate(paragraphs):
        all_chunks.append(para)
        all_ids.append(f"{doc_path.stem}_{i}")
        all_metadata.append({"source": doc_path.name})

print(f"共加载 {len(all_chunks)} 个文档块\n")

# --- Step 2: 存入向量库 ---
rag_collection = chroma.create_collection(name="rag_demo")
rag_collection.add(
    documents=all_chunks,
    ids=all_ids,
    metadatas=all_metadata,
)

# --- Step 3: 用户提问 → 检索 ---
question = "React 的常用 Hooks 有哪些？"
results = rag_collection.query(query_texts=[question], n_results=3)

print(f"问题: {question}")
print(f"检索到 {len(results['documents'][0])} 个相关片段:\n")
for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    print(f"  来源: {meta['source']}")
    print(f"  内容: {doc[:100]}...")
    print()

# --- Step 4: 拼接 prompt → 生成回答 ---
context = "\n\n---\n\n".join(results["documents"][0])
rag_prompt = f"""根据以下参考文档回答用户的问题。
如果文档中没有相关信息，明确说"根据现有文档无法回答"。
回答时引用文档中的具体内容。

参考文档：
{context}

用户问题：{question}"""

answer = ask(client_ai, MODEL, rag_prompt)
print(f"AI 回答:\n{answer}")
