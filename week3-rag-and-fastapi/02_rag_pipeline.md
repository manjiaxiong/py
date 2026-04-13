# Day 2: 最小 RAG 跑通 — 从文档到智能问答

## 学习目标

- 独立搭建一个完整的 RAG Pipeline（加载 → 分块 → 存储 → 检索 → 生成）
- 掌握 Chroma 持久化存储和 collection 管理
- 理解分块策略的取舍，能对比手写分块与 LangChain TextSplitter 的差异

## RAG Pipeline 完整流程图

```
  ┌─────────────────────────────────────────────────────────────┐
  │                   离线阶段（建索引）                          │
  │                                                             │
  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐ │
  │  │ 加载文档  │ → │ 文档分块  │ → │ Embedding │ → │ 存入   │ │
  │  │ .md 文件  │    │ chunk    │    │ 向量化    │    │ Chroma │ │
  │  └──────────┘    └──────────┘    └──────────┘    └───────┘ │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │                   在线阶段（回答问题）                        │
  │                                                             │
  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐ │
  │  │ 用户提问  │ → │ Embedding │ → │ 向量检索  │ → │ Top-K  │ │
  │  │ question  │    │ 向量化    │    │ 余弦相似  │    │ 结果   │ │
  │  └──────────┘    └──────────┘    └──────────┘    └───┬───┘ │
  │                                                      │     │
  │                  ┌──────────┐    ┌──────────┐        │     │
  │                  │  LLM 生成 │ ← │ 拼接     │ ←──────┘     │
  │                  │  回答     │    │ Prompt   │              │
  │                  └──────────┘    └──────────┘              │
  └─────────────────────────────────────────────────────────────┘
```

**JS 类比**：离线阶段 = `next build`（预处理），在线阶段 = `getServerSideProps`（实时请求）

## Chroma 核心 API

Chroma 是轻量级向量数据库，适合本地开发和小规模项目。

| API | 功能 | JS 类比 | 示例 |
|-----|------|---------|------|
| `collection.add()` | 添加文档（自动 embedding） | `db.insertMany()` | `collection.add(documents=[...], ids=[...], metadatas=[...])` |
| `collection.query()` | 语义检索 top-k | `db.find().sort().limit(k)` | `collection.query(query_texts=["问题"], n_results=3)` |
| `collection.get()` | 按 ID 精确获取 | `db.findById()` | `collection.get(ids=["doc_0", "doc_1"])` |
| `collection.delete()` | 删除文档 | `db.deleteMany()` | `collection.delete(ids=["doc_0"])` |
| `collection.update()` | 更新已有文档 | `db.updateMany()` | `collection.update(ids=["doc_0"], documents=["新内容"])` |
| `collection.count()` | 统计文档总数 | `db.countDocuments()` | `collection.count()` → `42` |

### 两种客户端模式

```python
# 内存模式（开发测试用，重启丢失）
# JS 类比: new Map()
client = chromadb.Client()

# 持久化模式（数据存磁盘，重启不丢）
# JS 类比: new Dexie("my_db") / SQLite
client = chromadb.PersistentClient(path="./chroma_db")
```

### Collection 创建方式

```python
# 创建（已存在会报错）
collection = client.create_collection("docs")

# 获取（不存在会报错）
collection = client.get_collection("docs")

# 推荐：获取或创建（不会报错）
collection = client.get_or_create_collection("docs")

# 删除 collection
client.delete_collection("docs")
```

## LangChain TextSplitter 对比手写分块

| 对比项 | 手写分块 | LangChain RecursiveCharacterTextSplitter |
|--------|---------|----------------------------------------|
| 实现难度 | 10 行代码 | `pip install` + 3 行代码 |
| 切分逻辑 | 固定字数滑窗 | 递归切分（段落→行→词→字符） |
| 语义保留 | 可能在句子中间切断 | 尽量在语义边界切（换行、句号） |
| 灵活度 | 完全自定义 | 可配置 separators 和 chunk_size |
| 适用场景 | 简单项目、学习原理 | 生产项目、复杂文档 |
| 依赖 | 无 | 需要 `langchain-text-splitters` |

### 手写分块代码

```python
def chunk_documents(text, chunk_size=400, overlap=80):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if len(chunk.strip()) > 20:
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks
```

**JS 类比**：`text.match(/.{1,400}/gs)` 但带 overlap

### LangChain TextSplitter 代码

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
    separators=["\n\n", "\n", " ", ""],  # 优先在段落→行→词处切分
)

chunks = splitter.split_text(text)
```

**JS 类比**：就像 `lodash.chunk()` 但更聪明——优先在句号、换行处切

### 分块参数怎么选？

| 参数 | 推荐值 | 太小了 | 太大了 |
|------|--------|--------|--------|
| chunk_size | 300~500 字 | 上下文不完整，检索到碎片 | 噪音多，不够精确 |
| chunk_overlap | 50~100 字 | 边界信息丢失 | 冗余太多，浪费存储 |

## JS 类比总览

| RAG 概念 | JS/前端类比 | 说明 |
|----------|------------|------|
| Chroma | MongoDB / IndexedDB | 存数据的数据库 |
| Collection | MongoDB Collection / DB Table | 一类数据的集合 |
| `collection.add()` | `db.insertMany()` | 批量插入数据 |
| `collection.query()` | `db.find({ $text: ... })` | 搜索，但这里是语义搜索 |
| Embedding | 给文本生成"语义指纹" | 文本 → 数字向量 |
| chunk_size | `str.slice(0, 400)` | 每块的最大长度 |
| overlap | 滑动窗口的重叠区域 | 防止信息被切断 |
| PersistentClient | SQLite / IndexedDB | 持久化存储 |
| `n_results` | `.limit(3)` | 返回前几条结果 |
| RAG Prompt | 模板字符串拼接 | `` `根据${context}回答${question}` `` |

## 关键要点

1. **持久化很重要** — 开发阶段用 `PersistentClient`，避免每次重启都重新建索引。生产环境可以用 Chroma Server 或 Pinecone 等云服务。

2. **分块策略决定检索质量** — chunk_size 太大噪音多，太小上下文不完整。300-500 字是中文文档的常用范围。overlap 50-100 字防止关键信息被切断。

3. **元数据是溯源的关键** — 给每个 chunk 加上 `source` 元数据（来源文件名），RAG 回答时能告诉用户"这个信息来自哪个文档"，大幅提升可信度。

4. **prompt 工程影响回答质量** — RAG 的 prompt 必须明确要求"只根据给定文档回答，不要编造"，否则 LLM 可能混入自己的知识，违背 RAG 的初衷。

5. **默认 embedding 够用就行** — Chroma 自带 `all-MiniLM-L6-v2` 模型，本地运行不花钱。对中文支持一般，生产项目可换成 `text2vec-base-chinese` 或调用 OpenAI embedding API。

## 推荐资源

- [Chroma 官方文档](https://docs.trychroma.com/) — API 参考和部署指南
- [LangChain Text Splitters](https://python.langchain.com/docs/how_to/#text-splitters) — 各种分块策略的文档
- [RAG 最佳实践（LangChain）](https://python.langchain.com/docs/tutorials/rag/) — 官方 RAG 教程
- [Chunking 策略对比](https://www.pinecone.io/learn/chunking-strategies/) — Pinecone 的分块策略详解
- [MTEB 排行榜](https://huggingface.co/spaces/mteb/leaderboard) — 各 Embedding 模型的评测排名
