# ===========================================
# rag.py — RAG Pipeline 封装
# ===========================================
# 提供：分块、索引、检索、问答
# ===========================================

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import get_client, ask

import chromadb


class RAGPipeline:
    """
    RAG Pipeline 封装

    JS 类比：
    class RAGPipeline {
        constructor() { this.collection = null; this.client = null; }
        async init() { /* 初始化 */ }
        index(text, source) { /* 索引 */ }
        async ask(question, topK) { /* 问答 */ }
    }
    """

    def __init__(self, collection_name="docs_copilot"):
        self.collection_name = collection_name
        self.chroma = chromadb.Client()
        self.collection = None
        self.ai_client = None
        self.model = None

    def init(self, env_path=None):
        """
        初始化：创建 collection + AI 客户端

        参数:
            env_path: .env 文件路径
        """
        # 初始化向量库
        try:
            self.chroma.delete_collection(self.collection_name)
        except Exception:
            pass

        self.collection = self.chroma.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # 初始化 AI 客户端
        if env_path:
            self.ai_client, self.model = get_client(env_path)
        else:
            self.ai_client, self.model = get_client(Path(__file__).parent / ".env")

        return self

    def index_text(self, text, source="unknown", chunk_size=500):
        """
        索引一段文本

        流程：按段落分块 → 存入向量库

        参数:
            text: 文档内容
            source: 来源标识
            chunk_size: 分块大小

        返回:
            分块数量
        """
        # 按段落分块
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and len(p.strip()) > 20]

        if not paragraphs:
            # 如果没有段落分隔，按固定大小分块
            paragraphs = []
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size].strip()
                if chunk:
                    paragraphs.append(chunk)

        if not paragraphs:
            return 0

        # 存入向量库
        import hashlib
        base_id = hashlib.md5(source.encode()).hexdigest()[:8]
        ids = [f"{base_id}_{i}" for i in range(len(paragraphs))]
        metadatas = [
            {"source": source, "chunk_index": i, "preview": p[:100]}
            for i, p in enumerate(paragraphs)
        ]

        self.collection.add(
            documents=paragraphs,
            ids=ids,
            metadatas=metadatas,
        )

        return len(paragraphs)

    def index_directory(self, directory):
        """
        索引目录下所有 .md 文件

        参数:
            directory: 文档目录路径

        返回:
            {"total_chunks": int, "files": int}
        """
        doc_dir = Path(directory)
        total = 0
        file_count = 0

        for doc_path in doc_dir.glob("*.md"):
            text = doc_path.read_text(encoding="utf-8")
            chunks = self.index_text(text, source=doc_path.name)
            total += chunks
            file_count += 1

        return {"total_chunks": total, "files": file_count}

    def search(self, question, n_results=3):
        """
        检索相关文档

        参数:
            question: 用户问题
            n_results: 返回结果数

        返回:
            {
                "context": "拼接的上下文字符串",
                "sources": [{"source": "...", "preview": "...", "relevance": 0.8}]
            }
        """
        if self.collection.count() == 0:
            return {"context": "", "sources": []}

        results = self.collection.query(
            query_texts=[question],
            n_results=min(n_results, self.collection.count()),
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        context = "\n\n---\n\n".join(documents)
        sources = [
            {
                "source": meta.get("source", "unknown"),
                "preview": meta.get("preview", ""),
                "relevance": round(1 / (1 + dist), 4) if dist >= 0 else 0,
            }
            for meta, dist in zip(metadatas, distances)
        ]

        return {"context": context, "sources": sources}

    def ask(self, question, n_results=3, max_tokens=1024):
        """
        完整的 RAG 问答

        流程：检索 → 拼接上下文 → 构造 prompt → 调 LLM

        参数:
            question: 用户问题
            n_results: 检索结果数
            max_tokens: 最大生成 token 数

        返回:
            {
                "answer": "AI 回答",
                "sources": [...],
                "question": "原始问题"
            }
        """
        # 检索
        search_result = self.search(question, n_results)

        if not search_result["context"]:
            return {
                "answer": "知识库为空，请先通过 /index 接口或 indexer.py 添加文档。",
                "sources": [],
                "question": question,
            }

        # 构造 RAG prompt
        context = search_result["context"]
        rag_prompt = f"""你是一个知识助手。根据以下参考文档回答用户的问题。
规则：
1. 只基于文档内容回答，不要编造
2. 如果文档中没有相关信息，明确说"根据现有文档无法回答这个问题"
3. 回答要简洁清晰
4. 适当引用文档中的原文

参考文档：
{context}

用户问题：{question}"""

        # 生成回答
        answer = ask(self.ai_client, self.model, rag_prompt, max_tokens=max_tokens)

        return {
            "answer": answer,
            "sources": search_result["sources"],
            "question": question,
        }

    def ask_with_threshold(self, question, n_results=5, threshold=1.0, max_tokens=1024):
        """
        带相似度阈值过滤的 RAG 问答

        参数:
            question: 用户问题
            n_results: 最大检索数
            threshold: 距离阈值（余弦距离下 1-threshold 为最低相似度）
            max_tokens: 最大生成 token 数
        """
        if self.collection.count() == 0:
            return {
                "answer": "知识库为空",
                "sources": [],
                "question": question,
            }

        results = self.collection.query(
            query_texts=[question],
            n_results=min(n_results, self.collection.count()),
        )

        # 过滤
        filtered_docs = []
        filtered_metas = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if dist < threshold:
                filtered_docs.append(doc)
                filtered_metas.append(meta)

        if not filtered_docs:
            return {
                "answer": "文档中未找到相关信息，无法回答该问题。",
                "sources": [],
                "question": question,
            }

        context = "\n\n---\n\n".join(
            f"[来源: {m['source']}]\n{d}" for d, m in zip(filtered_docs, filtered_metas)
        )

        rag_prompt = f"""根据以下参考文档回答用户问题。只使用文档中的信息。

参考文档：
{context}

用户问题：{question}"""

        answer = ask(self.ai_client, self.model, rag_prompt, max_tokens=max_tokens)

        sources = [
            {
                "source": m.get("source", "unknown"),
                "preview": m.get("preview", ""),
                "relevance": round(1 / (1 + d), 4),
            }
            for m, d in zip(filtered_metas, [0] * len(filtered_metas))
        ]

        return {
            "answer": answer,
            "sources": sources,
            "question": question,
        }


# 全局实例（供 main.py 使用）
pipeline = None


def get_pipeline():
    """获取或初始化全局 RAG Pipeline"""
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline().init(Path(__file__).parent / ".env")
    return pipeline
