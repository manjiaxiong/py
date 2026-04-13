# ===========================================
# 练习 2：最小 RAG Pipeline（对应 Day 2）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 02_rag_pipeline.py / 02_rag_pipeline.md
# ===========================================

import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask


# --- 题目 1: 加载文档 ---

# TODO 1.1: 从 sample_docs 目录读取所有 .md 文件，合并成一个大字符串
doc_dir = Path(__file__).parent.parent / "week3-rag-and-fastapi" / "sample_docs"

def load_docs(directory):
    """读取目录下所有 .md 文件，返回 {文件名: 内容} 的字典"""
    docs = {}
    # TODO: 用 Path(directory).glob("*.md") 遍历，read_text 读取
    pass
    return docs


# 测试
# docs = load_docs(doc_dir)
# print(f"加载了 {len(docs)} 个文档文件")
# for name, content in docs.items():
#     print(f"  {name}: {len(content)} 字符")


# --- 题目 2: 文档分块 ---

# TODO 2.1: 完善分块函数
def chunk_docs(docs, chunk_size=500, overlap=50):
    """
    把多个文档分块

    参数:
        docs: {文件名: 内容} 的字典
        chunk_size: 每块大小
        overlap: 重叠字符数

    返回:
        {
            "chunks": [块1, 块2, ...],
            "ids": ["doc1_0", "doc1_1", ...],
            "metadatas": [{"source": "doc1.md"}, ...],
        }
    """
    chunks = []
    ids = []
    metadatas = []

    for doc_name, content in docs.items():
        # TODO: 按段落分块（split("\n\n")），过滤太短的
        # 然后给每块生成 id 和 metadata
        pass

    return {"chunks": chunks, "ids": ids, "metadatas": metadatas}


# --- 题目 3: 存入向量库 ---

import chromadb

# TODO 3.1: 创建 Chroma 内存客户端
# TODO 3.2: 创建名为 "practice_rag" 的 collection
# TODO 3.3: 把 chunk_docs 返回的数据存入 collection


def store_chunks(collection, chunks_data):
    """
    把分块结果存入向量库

    参数:
        collection: Chroma collection
        chunks_data: chunk_docs() 返回的字典
    """
    # TODO: 调用 collection.add(documents=..., ids=..., metadatas=...)
    pass


# --- 题目 4: 检索测试 ---

# TODO 4.1: 封装检索函数
def search(collection, query, n_results=3):
    """
    检索相关文档

    返回:
        [
            {"content": "文档内容", "source": "来源", "distance": 0.5},
            ...
        ]
    """
    # TODO: 调用 collection.query，整理结果
    pass


# 测试
# results = search(collection, "React Hooks 有哪些？")
# for r in results:
#     print(f"[{r['distance']:.4f}] 来源: {r['source']}")
#     print(f"  内容: {r['content'][:80]}...")


# --- 题目 5: RAG 问答 ---

# TODO 5.1: 封装完整的 RAG 问答函数
def rag_ask(collection, client, model, question, n_results=3):
    """
    完整的 RAG 问答

    流程：
    1. 检索相关文档
    2. 拼接上下文
    3. 构造 RAG prompt
    4. 调 LLM 生成回答
    5. 返回 {answer, sources, question}
    """
    # TODO: 实现 RAG 问答
    # prompt 模板：
    # f"""根据以下参考文档回答用户问题。
    # 如果文档中没有相关信息，说"文档中未提及"。
    #
    # 参考文档：
    # {context}
    #
    # 用户问题：{question}"""
    pass


# 测试
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
# result = rag_ask(collection, client_ai, MODEL, "Python 的异步编程怎么用？")
# print(f"回答: {result['answer'][:200]}")
# print(f"来源: {result['sources']}")
