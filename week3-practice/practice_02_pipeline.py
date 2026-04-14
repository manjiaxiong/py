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

doc_dir = Path(__file__).parent.parent / "week3-rag-and-fastapi" / "sample_docs"

def load_docs(directory):
    """读取目录下所有 .md 文件，返回 {文件名: 内容} 的字典"""
    docs = {}
    for md_file in Path(directory).glob("*.md"):
        docs[md_file.name] = md_file.read_text(encoding="utf-8")
    return docs


# 测试
docs = load_docs(doc_dir)
print("=== 题目 1: 加载文档 ===")
print(f"加载了 {len(docs)} 个文档文件")
for name, content in docs.items():
    print(f"  {name}: {len(content)} 字符")


# --- 题目 2: 文档分块 ---

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
        # 按段落分块
        paragraphs = content.split("\n\n")
        current_chunk = ""
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) > chunk_size:
                # 保存当前块
                if len(current_chunk) >= 30:
                    chunks.append(current_chunk)
                    ids.append(f"{doc_name.replace('.md', '')}_{chunk_idx}")
                    metadatas.append({"source": doc_name})
                    chunk_idx += 1
                # 新块从重叠开始
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # 保存最后一个块
        if len(current_chunk) >= 30:
            chunks.append(current_chunk)
            ids.append(f"{doc_name.replace('.md', '')}_{chunk_idx}")
            metadatas.append({"source": doc_name})

    return {"chunks": chunks, "ids": ids, "metadatas": metadatas}


# 测试
chunks_data = chunk_docs(docs, chunk_size=500, overlap=50)
print(f"\n=== 题目 2: 文档分块 ===")
print(f"共 {len(chunks_data['chunks'])} 个块")
for i, (chunk, src) in enumerate(zip(chunks_data["chunks"], chunks_data["metadatas"])):
    print(f"  [{i}] 来源: {src['source']}, 长度: {len(chunk)}")
    print(f"      预览: {chunk[:60]}...")


# --- 题目 3: 存入向量库 ---

import chromadb

# 创建 Chroma 内存客户端
chroma = chromadb.Client()
collection = chroma.create_collection(name="practice_rag")


def store_chunks(collection, chunks_data):
    """
    把分块结果存入向量库

    参数:
        collection: Chroma collection
        chunks_data: chunk_docs() 返回的字典
    """
    collection.add(
        documents=chunks_data["chunks"],
        ids=chunks_data["ids"],
        metadatas=chunks_data["metadatas"],
    )
    print(f"  已存入 {len(chunks_data['chunks'])} 个块到向量库")


# 测试
store_chunks(collection, chunks_data)


# --- 题目 4: 检索测试 ---

def search(collection, query, n_results=3):
    """
    检索相关文档

    返回:
        [
            {"content": "文档内容", "source": "来源", "distance": 0.5},
            ...
        ]
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    return [
        {
            "content": doc,
            "source": meta.get("source", ""),
            "distance": dist,
        }
        for doc, meta, dist in zip(docs, metas, dists)
    ]


# 测试
results = search(collection, "React Hooks 有哪些？")
print(f"\n=== 题目 4: 检索测试 ===")
for r in results:
    print(f"[{r['distance']:.4f}] 来源: {r['source']}")
    print(f"  内容: {r['content'][:80]}...")


# --- 题目 5: RAG 问答 ---

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
    # 检索
    results = search(collection, question, n_results=n_results)
    context = "\n\n---\n\n".join(r["content"] for r in results)
    sources = [{"source": r["source"], "distance": r["distance"]} for r in results]

    # 构造 prompt
    prompt = f"""根据以下参考文档回答用户问题。
如果文档中没有相关信息，请说"文档中未提及"。

参考文档：
{context}

用户问题：{question}"""

    # 调 LLM
    answer = ask(client, model, prompt, max_tokens=800)

    return {
        "answer": answer,
        "sources": sources,
        "question": question,
    }


# 测试
client_ai, MODEL = get_client(Path(__file__).parent / ".env")
result = rag_ask(collection, client_ai, MODEL, "Python 的异步编程怎么用？")
print(f"\n=== 题目 5: RAG 问答 ===")
print(f"问题: {result['question']}")
print(f"回答: {result['answer'][:200]}...")
print(f"来源: {result['sources']}")
