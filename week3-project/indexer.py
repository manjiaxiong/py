# ===========================================
# indexer.py — 文档索引脚本
# ===========================================
# 把 docs/ 目录下的所有 .md 文件索引到向量库
# 用法: python week3-project/indexer.py
# ===========================================

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag import RAGPipeline


def main():
    docs_dir = Path(__file__).parent / "docs"

    if not docs_dir.exists():
        print(f"错误: 文档目录不存在: {docs_dir}")
        print("请先在 docs/ 目录下放置 .md 文件")
        return

    # 检查是否有文件
    md_files = list(docs_dir.glob("*.md"))
    if not md_files:
        print(f"错误: docs/ 目录下没有找到 .md 文件")
        print("可以复制 week3-rag-and-fastapi/sample_docs/ 的文件到 docs/")
        return

    print(f"找到 {len(md_files)} 个文档文件:")
    for f in md_files:
        print(f"  - {f.name} ({f.stat().st_size} 字符)")
    print()

    # 初始化 pipeline
    print("初始化 RAG Pipeline...")
    pipeline = RAGPipeline().init(Path(__file__).parent / ".env")

    # 索引文档
    print("开始索引...")
    result = pipeline.index_directory(docs_dir)

    print(f"\n索引完成:")
    print(f"  文件数: {result['files']}")
    print(f"  分块数: {result['total_chunks']}")
    print(f"  集合名: {pipeline.collection_name}")

    # 验证
    count = pipeline.collection.count()
    print(f"\n向量库验证: 共 {count} 条文档")

    # 测试检索
    if count > 0:
        print("\n检索测试:")
        test_queries = ["React Hooks", "API 设计", "Python"]
        for q in test_queries:
            result = pipeline.search(q, n_results=1)
            if result["sources"]:
                src = result["sources"][0]
                print(f"  '{q}' → 最近来源: {src['source']} (相关度: {src['relevance']:.2%})")
            else:
                print(f"  '{q}' → 无结果")


if __name__ == "__main__":
    main()
