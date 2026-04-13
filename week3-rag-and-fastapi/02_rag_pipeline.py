# ===========================================
# Day 2: 最小 RAG 跑通 — 从文档到智能问答
# ===========================================
# 今天目标：把 Day 1 学的零散概念串成一个完整的 RAG Pipeline
# 从"读文件 → 分块 → 存向量库 → 检索 → 生成回答"一步步走通
#
# 前端类比：
# RAG Pipeline 就像一个完整的搜索引擎：
# 1. 爬虫（加载文档） → 2. 建索引（分块 + embedding + 存库）
# 3. 搜索（检索） → 4. 展示（LLM 生成回答）
#
# JS 类比：
# 这就像你用 Elasticsearch 搭一个全文搜索，但搜的是"语义"不是"关键词"
# 整个流程 = Next.js 的 getStaticProps（预处理）+ getServerSideProps（实时查询）
# ===========================================

# 安装（如果还没装）：
# pip install chromadb langchain-text-splitters

import sys
from pathlib import Path
from dotenv import load_dotenv

# --- 跨目录导入 utils ---
# JS 类比: 就像 tsconfig 的 paths 配置，让 import 能找到上层目录
sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

import chromadb


# ===========================================
# 1. 初始化 Chroma — 创建持久化向量数据库
# ===========================================
# Day 1 用的是 chromadb.Client()（内存模式，重启就没了）
# 今天用 PersistentClient（数据存磁盘，重启还在）
#
# JS 类比：
# chromadb.Client()         = Map()（内存中，刷新就没了）
# chromadb.PersistentClient = SQLite / IndexedDB（持久化）
#
# Collection 概念：
# collection = 数据库的 table = MongoDB 的 collection
# 一个 collection 存一类文档的向量

print("=== 1. 初始化 Chroma 向量数据库 ===\n")

# persist_directory: 数据存在哪个文件夹
# JS 类比: new Dexie("my_db") 指定 IndexedDB 数据库名
chroma_client = chromadb.PersistentClient(
    path=str(Path(__file__).parent / "chroma_db")
)

# get_or_create_collection: 有就用，没有就创建
# JS 类比: db.createObjectStore("docs") 但不会重复创建
# 注意：如果之前运行过，这里会直接拿到已有的 collection
collection = chroma_client.get_or_create_collection(
    name="my_docs",                              # collection 名称
    metadata={"hnsw:space": "cosine"},           # 用余弦相似度（比 L2 距离更直觉）
)

print(f"Collection 名称: {collection.name}")
print(f"已有文档数量: {collection.count()}")
print(f"存储路径: {Path(__file__).parent / 'chroma_db'}\n")


# ===========================================
# 2. 加载文档 — 读取 sample_docs/ 下的所有 .md 文件
# ===========================================
# 用 pathlib 遍历目录，读取所有 Markdown 文件
#
# JS 类比：
# const files = fs.readdirSync("./sample_docs").filter(f => f.endsWith(".md"));
# const docs = files.map(f => ({ name: f, content: fs.readFileSync(f, "utf-8") }));

print("\n=== 2. 加载文档 ===\n")

doc_dir = Path(__file__).parent / "sample_docs"

# glob("*.md") = 查找所有 .md 文件
# JS 类比: require("glob").sync("*.md")
documents = {}
for doc_path in sorted(doc_dir.glob("*.md")):
    content = doc_path.read_text(encoding="utf-8")
    documents[doc_path.name] = content
    print(f"  已加载: {doc_path.name} ({len(content)} 字符)")

print(f"\n共加载 {len(documents)} 个文档")


# ===========================================
# 3. 文档分块 — 把长文档切成小块
# ===========================================
# 为什么要分块？
# 1. LLM 的 context window 有限（不能塞整篇文档）
# 2. 小块检索更精确（整篇文档 vs 一个段落，后者更有针对性）
# 3. embedding 对短文本效果更好
#
# 两种方式对比：
# - 手写分块：灵活可控，适合简单场景
# - LangChain TextSplitter：开箱即用，处理边界更好
#
# JS 类比：
# 手写分块 = 自己写 string.slice() 循环
# LangChain = 用 lodash.chunk()，省心省力

print("\n=== 3. 文档分块 ===\n")

# --- 方法 1: 手写分块（带重叠） ---
def chunk_documents(text, chunk_size=400, overlap=80):
    """
    将文本按固定大小分块，相邻块之间有重叠

    参数:
        text: 原始文本
        chunk_size: 每块最大字符数（= 一个"页面"的大小）
        overlap: 重叠字符数（防止关键信息被切断）

    返回:
        list[str] — 分好的文本块

    JS 类比：
    function chunkDocuments(text, chunkSize = 400, overlap = 80) {
        const chunks = [];
        let start = 0;
        while (start < text.length) {
            chunks.push(text.slice(start, start + chunkSize));
            start += chunkSize - overlap;
        }
        return chunks;
    }
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # 跳过太短的块（可能是尾部碎片）
        if len(chunk.strip()) > 20:
            chunks.append(chunk.strip())
        start += chunk_size - overlap  # 向前滑动，保留 overlap 重叠
    return chunks

# 对所有文档进行分块
all_chunks = []     # 所有文本块
all_ids = []        # 每个块的唯一 ID
all_metadatas = []  # 每个块的元数据（来源文件名）

for filename, content in documents.items():
    chunks = chunk_documents(content, chunk_size=400, overlap=80)
    for i, chunk in enumerate(chunks):
        all_chunks.append(chunk)
        all_ids.append(f"{filename}_{i}")           # 唯一 ID: "react_basics.md_0"
        all_metadatas.append({"source": filename})   # 元数据: 来源文件名

print(f"手写分块结果: 共 {len(all_chunks)} 个块\n")
for i, (chunk, meta) in enumerate(zip(all_chunks[:3], all_metadatas[:3])):
    print(f"  块 {i} (来自 {meta['source']}): {chunk[:60]}...")

# # --- 方法 2: LangChain RecursiveCharacterTextSplitter ---
# # 递归切分：先按 \n\n（段落），再按 \n（行），再按 " "（词），最后按字符
# # 尽量在语义边界切分，比手写的更智能
# #
# # JS 类比：这就像 lodash.chunk() 但更聪明——它会在句号、换行处切，
# # 而不是在一个单词中间切断
#
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,          # 每块最大字符数
    chunk_overlap=80,        # 重叠字符数
    separators=["\n\n", "\n", " ", ""],  # 优先在这些位置切分
)

# LangChain 分块示例
lc_chunks = []
lc_ids = []
lc_metadatas = []

for filename, content in documents.items():
    chunks = splitter.split_text(content)
    for i, chunk in enumerate(chunks):
        lc_chunks.append(chunk)
        lc_ids.append(f"lc_{filename}_{i}")
        lc_metadatas.append({"source": filename})

print(f"\nLangChain 分块结果: 共 {len(lc_chunks)} 个块")
print(f"对比: 手写 {len(all_chunks)} 块 vs LangChain {len(lc_chunks)} 块\n")
for i, (chunk, meta) in enumerate(zip(lc_chunks[:3], lc_metadatas[:3])):
    print(f"  块 {i} (来自 {meta['source']}): {chunk[:60]}...")


# ===========================================
# 4. 存入向量库 — 把分好的块 + 元数据写入 Chroma
# ===========================================
# Chroma 的 add() 方法会自动做 embedding（用默认模型）
# 不需要手动调 embedding API，省钱！
#
# 核心概念：
# - documents: 原始文本（Chroma 存下来方便查看）
# - ids: 每条文档的唯一 ID（= 数据库的主键）
# - metadatas: 元数据（来源文件名等，方便溯源）
#
# JS 类比：
# collection.add() = db.collection("docs").insertMany(docs)
# ids              = MongoDB 的 _id 字段
# metadatas        = 额外的索引字段

print("\n=== 4. 存入向量库 ===\n")

# 如果 collection 已有数据，先清空再重新写入
# JS 类比: await db.collection("docs").deleteMany({})
print(f"Collection 当前已有 {collection.count()} 条数据")  # 如果之前运行过，这里会显示之前的数量
if collection.count() > 0:
    # 获取所有已有 ID 并删除
    existing = collection.get()
    print(f"Collection 已有 {len(existing['ids'])} 条数据，正在清空...")
    collection.delete(ids=existing["ids"])
    print(f"已清空旧数据 ({len(existing['ids'])} 条)\n")

# 写入向量库
# JS 类比: await db.collection("docs").insertMany(chunks.map((chunk, i) => ({
#     _id: ids[i], text: chunk, metadata: metadatas[i]
# })))
collection.add(
    documents=all_chunks,    # 文本内容
    ids=all_ids,             # 唯一 ID
    metadatas=all_metadatas, # 元数据
)

print(f"成功写入 {collection.count()} 条文档到向量库")
print(f"存储路径: {Path(__file__).parent / 'chroma_db'}")
print("重启程序后数据不会丢失（持久化存储）\n")


# ===========================================
# 5. 检索测试 — 用自然语言查询，看返回结果
# ===========================================
# collection.query() 做了三件事：
# 1. 把你的查询文本做 embedding（变成向量）
# 2. 在向量库中找最相似的 k 条
# 3. 返回文本 + 元数据 + 距离分数
#
# 距离分数（cosine 模式）：
# 0 = 完全相同，2 = 完全不同
# 余弦相似度 = 1 - distance（0~1，越大越相似）
#
# JS 类比：
# collection.query()  = db.collection("docs").find({ $text: { $search: query } })
# 但这里是语义搜索，不是关键词搜索！
# "前端框架" 能搜到 "React"（关键词搜索做不到）

print("\n=== 5. 检索测试 ===\n")

test_queries = [
    "React 有哪些常用的 Hooks？",
    "Python 怎么处理异常？",
    "API 接口应该怎么设计？",
    "怎么做性能优化？",           # 跨文档查询——React 和 Python 都有相关内容
]

for query in test_queries:
    results = collection.query(
        query_texts=[query],   # 查询文本（会自动做 embedding）
        n_results=3,           # 返回 top-3（= LIMIT 3）
    )

    print(f"查询: '{query}'")
    print(f"返回 {len(results['documents'][0])} 条结果:")

    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        similarity = 1 - dist   # cosine distance → similarity
        print(f"  {i+1}. [{similarity:.2%}] 来源: {meta['source']}")
        print(f"     {doc[:80]}...")
    print()


# ===========================================
# 6. RAG 问答 — 完整 Pipeline: 检索 → 拼接 → 生成
# ===========================================
# 这是整个 RAG 的核心流程：
# 1. 用户提问
# 2. 从向量库检索相关文档块（top-k）
# 3. 把检索到的块拼成 context
# 4. 构造 prompt（system + context + question）
# 5. 调 LLM 生成回答
# 6. 展示回答 + 引用来源
#
# JS 类比：
# async function ragChat(question) {
#     const docs = await vectorDB.search(question, { limit: 3 });  // 检索
#     const context = docs.map(d => d.text).join("\n\n");           // 拼接
#     const prompt = `根据文档回答: ${context}\n\n问题: ${question}`; // 构造
#     const answer = await openai.chat(prompt);                     // 生成
#     return { answer, sources: docs.map(d => d.source) };          // 返回
# }

# print("\n=== 6. RAG 问答（完整 Pipeline）===\n")
#
# # --- 初始化 LLM 客户端 ---
# client_ai, MODEL = get_client(Path(__file__).parent / ".env")
#
# def rag_query(question, n_results=3):
#     """
#     完整 RAG 问答函数
#
#     流程: 检索 → 构造 prompt → 调 LLM → 返回回答 + 来源
#
#     参数:
#         question: 用户的问题
#         n_results: 检索多少条相关文档（top-k）
#
#     返回:
#         (answer, sources) — 回答文本 + 引用来源列表
#
#     JS 类比：
#     async function ragQuery(question, nResults = 3) {
#         const results = await collection.query(question, nResults);
#         const context = results.documents.join("\n\n---\n\n");
#         const answer = await llm.chat(buildPrompt(context, question));
#         const sources = [...new Set(results.metadatas.map(m => m.source))];
#         return { answer, sources };
#     }
#     """
#     # Step 1: 检索相关文档
#     results = collection.query(
#         query_texts=[question],
#         n_results=n_results,
#     )
#
#     # Step 2: 拼接 context（用分隔线隔开多个文档块）
#     # JS 类比: docs.join("\n\n---\n\n")
#     context = "\n\n---\n\n".join(results["documents"][0])
#
#     # Step 3: 构造 RAG prompt
#     # 关键：告诉 AI "只根据给定文档回答"，不要编造
#     rag_prompt = f"""请根据以下参考文档回答用户的问题。
#
# 要求：
# 1. 只使用参考文档中的信息回答，不要编造
# 2. 如果文档中没有相关信息，明确说"根据现有文档无法回答这个问题"
# 3. 回答时引用文档中的具体内容
# 4. 用简洁清晰的中文回答
#
# 参考文档：
# {context}
#
# 用户问题：{question}"""
#
#     # Step 4: 调 LLM 生成回答
#     answer = ask(client_ai, MODEL, rag_prompt, max_tokens=800)
#
#     # Step 5: 收集来源（去重）
#     # JS 类比: [...new Set(metadatas.map(m => m.source))]
#     sources = list(set(
#         meta["source"] for meta in results["metadatas"][0]
#     ))
#
#     return answer, sources
#
#
# # --- 测试 RAG 问答 ---
# questions = [
#     "React 中 useEffect 有什么用？怎么用？",
#     "Python 有哪些常用的数据结构操作技巧？",
#     "设计 RESTful API 时，状态码应该怎么选择？",
# ]
#
# for q in questions:
#     print(f"问题: {q}")
#     print("-" * 50)
#
#     answer, sources = rag_query(q)
#
#     print(f"回答:\n{answer}\n")
#     print(f"引用来源: {', '.join(sources)}")
#     print("=" * 60 + "\n")
