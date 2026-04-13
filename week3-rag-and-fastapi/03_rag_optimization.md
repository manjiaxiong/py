# Day 3: RAG 优化 — 从"能用"到"好用"

## 学习目标

- 理解 chunk_size 对检索效果的影响，能通过实验选择合适的大小
- 掌握 top-k 参数的调优方法
- 实现引用来源展示和相似度阈值过滤
- 理解 Rerank（二次排序）的概念和适用场景
- 建立 RAG 评估流程，分开评估检索和生成质量

## 为什么需要优化？

Day 1 搭了一个能跑的 RAG，但实际效果可能不理想：
- 检索结果不精准（返回了不相关的片段）
- 回答不完整（漏掉了关键信息）
- 回答有幻觉（基于不相关内容编造答案）

**前端类比**：Day 1 = 写了个能跑的页面（没做性能优化），今天 = 做 Lighthouse 优化、做 SEO、做缓存策略。

## 关键参数一览

| 参数 | 含义 | 常见范围 | 影响 |
|------|------|----------|------|
| chunk_size | 文档块大小 | 200-1000 字符 | 检索精度 vs 上下文完整性 |
| overlap | 块间重叠 | 50-100 字符 | 防止关键信息被切断 |
| top_k | 返回结果数 | 3-5 条 | 回答完整性 vs 噪音 |
| threshold | 距离阈值 | 1.0-1.5（L2） | 过滤不相关结果 |

## 1. Chunk 大小实验

分块大小是 RAG 效果的第一个关键因素：

| 块大小 | 优点 | 缺点 | 适用场景 |
|--------|------|------|----------|
| 200 字符 | 精确、噪音少 | 语义可能不完整 | 短查询、关键词匹配 |
| 500 字符 | 平衡点 | — | 大多数场景（推荐起点） |
| 1000 字符 | 上下文完整 | 噪音多、浪费 token | 需要完整上下文的复杂问题 |

```python
# 分块函数
def chunk_by_size(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # 重叠，防止切断
    return chunks
```

**JS 类比**：就像你做搜索功能，索引粒度的选择 — 按整篇文章索引（太粗） vs 按每个单词索引（太细） vs 按段落索引（刚好）。

**实验方法**：用同一组 query，对比不同 chunk_size 的检索结果距离值。距离越小 = 越相关。

## 2. top-k 调整

top_k = 返回最相似的 k 条结果：

| k 值 | 效果 | 推荐 |
|------|------|------|
| k=1 | 可能不完整 | 仅用于演示 |
| k=3 | 信息充分、噪音少 | **推荐** |
| k=5+ | 信息最多，但引入噪音 | 文档量大时使用 |

```python
# 检索不同数量的结果
for k in [1, 3, 5]:
    results = collection.query(query_texts=[query], n_results=k)
    context = "\n\n---\n\n".join(results["documents"][0])
    # 用 context 构建 prompt → 调 LLM
```

**经验法则**：从 k=3 开始，如果回答经常不完整，增加到 5。

## 3. 引用来源展示

RAG 最大的优势之一：回答可以追溯到原始文档。

```python
# 建索引时存来源信息
all_metadatas.append({
    "source": doc_path.name,     # 来源文件名
    "chunk_index": i,            # 第几块
})

# 检索时返回来源
for doc, meta, dist in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0],
):
    print(f"来源: {meta['source']} (第 {meta['chunk_index']+1} 块)")
    print(f"距离: {dist:.4f}")
```

**前端类比**：就像搜索引擎的结果页 — 标题（AI 回答） + 来源链接（原始文档） + 摘要（原文片段）。

## 4. 相似度阈值过滤

问题：用户问了文档里完全没有的问题，向量库还是会返回"最相似"的结果，AI 可能基于不相关内容瞎答。

解决：设定距离阈值，超过阈值 → 拒绝回答。

```python
DISTANCE_THRESHOLD = 1.5  # 需要根据实际情况调整

for doc, dist in zip(results["documents"][0], results["distances"][0]):
    if dist < DISTANCE_THRESHOLD:
        # 通过阈值，可以回答
    else:
        # 未通过阈值，拒绝回答
```

Chroma L2 距离参考：
- < 0.5：非常相关
- 0.5 ~ 1.0：一般相关
- > 1.5：基本不相关

**带阈值过滤的 RAG 函数**：
```python
def rag_with_threshold(collection, query, client, model, n_results=3, threshold=1.5):
    results = collection.query(query_texts=[query], n_results=n_results)

    # 过滤不相关结果
    filtered = [(d, m) for d, m, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ) if dist < threshold]

    if not filtered:
        return "文档中未找到相关信息，无法回答该问题。"

    # 拼接上下文 → 调 LLM
    context = "\n\n---\n\n".join(f"[来源: {m['source']}]\n{d}" for d, m in filtered)
    return ask(client, model, f"根据以下文档回答问题...\n\n{context}\n\n问题：{query}")
```

## 5. Rerank 概念

向量检索只是粗排（recall），不一定精准。Rerank 是在检索之后用更精确的模型重新打分排序。

### Bi-encoder vs Cross-encoder

| 类型 | 方式 | 速度 | 精度 | 类比 |
|------|------|------|------|------|
| Bi-encoder | 文档和查询分别编码，算距离 | 快（可预计算） | 一般 | 简历关键词匹配 |
| Cross-encoder | 查询+文档一起输入，输出相关性 | 慢（一对一比较） | 高 | 面试深入评估 |

### 完整流程

```
Step 1: Bi-encoder 检索 top-20（快速召回）
Step 2: Cross-encoder 对这 20 条重新打分（精准排序）
Step 3: 取 top-3 送给 LLM
```

```python
# 伪代码
# Step 1: 粗排（我们已经会了）
candidates = collection.query(query, n_results=20)

# Step 2: 精排（Cross-encoder）
# from sentence_transformers import CrossEncoder
# reranker = CrossEncoder('BAAI/bge-reranker-base')
# pairs = [[query, doc] for doc in candidates]
# scores = reranker.predict(pairs)
# top3 = sorted(zip(scores, candidates), reverse=True)[:3]
```

**什么时候需要 Rerank？**
- 文档量 > 1000 条且检索精度不够时
- 简单项目不需要，先把 chunk_size 和 top_k 调好

常用方案：Cohere Rerank API（商业）、sentence-transformers CrossEncoder（开源）、bge-reranker（中文效果好）。

## 6. 评估 RAG

很多人做 RAG 全凭感觉调参数，正确做法：建评估集，用数据说话。

### 分开评估（关键概念！）

| 评估类型 | 问题 | 指标 | 类比 |
|----------|------|------|------|
| 检索评估 | 检索到的文档块是否正确？ | 命中率（Hit Rate） | 搜索引擎有没有把对的结果排在前面 |
| 生成评估 | AI 基于检索的回答是否正确？ | 关键词命中率 | AI 看了对的文档，有没有正确理解 |

**分开评估的好处**：
- 检索对了但回答错了 → 优化 prompt
- 检索错了 → 优化 chunk_size / embedding / rerank
- 两个都对了但用户不满意 → 优化回答格式

### 评估流程

```python
# 1. 定义评估集
eval_set = [
    {
        "question": "React 的常用 Hooks 有哪些？",
        "expected_source": "react_basics.md",
        "expected_keywords": ["useState", "useEffect", "useContext"],
    },
    ...
]

# 2. 运行评估
for item in eval_set:
    # 检索评估：期望来源是否在 top-k 中？
    retrieval_hit = expected_src in retrieved_sources

    # 生成评估：AI 回答中是否包含期望关键词？
    kw_hits = [kw for kw in expected_kws if kw in answer]
    generation_hit = len(kw_hits) >= len(expected_kws) // 2 + 1

# 3. 汇总
print(f"检索命中率: {retrieval_hits}/{total}")
print(f"生成通过率: {generation_hits}/{total}")
```

### 优化决策树

```
检索命中率低？
  ├── 是 → 调整 chunk_size、换 embedding 模型、加 rerank
  └── 否 → 生成通过率低？
             ├── 是 → 优化 prompt 模板、增加上下文、调整 top_k
             └── 否 → 两个都低 → 检查文档质量
```

## 推荐资源

- [Chroma 文档查询优化](https://docs.trychroma.com/docs/querying-collections)
- [LangChain 评估指南](https://python.langchain.com/docs/guides/evaluation/)
- [RAG 评估框架 — RAGAS](https://docs.ragas.io/)
