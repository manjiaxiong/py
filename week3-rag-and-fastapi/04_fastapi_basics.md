# Day 4: FastAPI 后端 — Python 版的 Express.js

## 学习目标

- 理解 FastAPI 和 Express.js 的对应关系
- 掌握 GET/POST 路由、路径参数、查询参数
- 熟练使用 Pydantic 做请求校验和响应序列化
- 实现 RAG 的 HTTP 接口（POST /ask + POST /index）
- 理解 SSE 流式输出的原理和实现
- 配置 CORS 和静态文件

## FastAPI vs Express.js 对比

| 功能 | Express | FastAPI |
|------|---------|---------|
| 创建应用 | `const app = express()` | `app = FastAPI()` |
| GET 路由 | `app.get("/path", fn)` | `@app.get("/path")` |
| POST 路由 | `app.post("/path", fn)` | `@app.post("/path")` |
| 路径参数 | `req.params.id` | 函数参数 `(id: int)` |
| 查询参数 | `req.query.page` | 函数参数 + 默认值 `(page=1)` |
| 请求体 | `req.body` + `express.json()` | Pydantic Model |
| 请求校验 | Zod / Joi（额外安装） | Pydantic（内置） |
| 响应 | `res.json({...})` | `return {...}` |
| 状态码 | `res.status(201).json(...)` | `JSONResponse(status_code=201, ...)` |
| 中间件 | `app.use(fn)` | `app.add_middleware()` |
| CORS | `app.use(cors())` | `app.add_middleware(CORSMiddleware, ...)` |
| 静态文件 | `app.use(express.static(...))` | `app.mount("/static", StaticFiles(...))` |
| API 文档 | Swagger 手动配置 | 自动生成 `/docs` |
| 异步 | `async/await` | `async/await` |
| 热重载 | `nodemon` | `uvicorn --reload` |

## 1. 第一个 FastAPI 应用

```python
from fastapi import FastAPI

app = FastAPI(
    title="AI RAG API",
    description="RAG 知识助手",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI!"}
```

启动命令：
```bash
uvicorn 04_fastapi_basics:app --reload
```

启动后访问：
- `http://localhost:8000` → API 根路径
- `http://localhost:8000/docs` → Swagger UI（自动生成！）
- `http://localhost:8000/redoc` → ReDoc 文档

## 2. GET 路由 — 路径参数 vs 查询参数

### 路径参数（Path Parameters）

```python
@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello, {name}!"}
```

Express 等价：`app.get("/hello/:name", ...)`，但 Express 要手动从 `req.params.name` 取值。FastAPI 直接写在函数参数里。

### 查询参数（Query Parameters）

```python
@app.get("/search")
def search(q: str, page: int = 1, limit: int = Query(default=10, le=100)):
    return {"query": q, "page": page, "limit": limit}
```

规则：
- **没有默认值 = 必填**（缺少返回 422）
- **有默认值 = 可选**
- `Query(le=100)` 额外约束（less than or equal）

Express 等价：需要手动从 `req.query` 取值 + 手动校验。FastAPI 自动完成。

## 3. 请求体 + Pydantic — POST 请求

Express 需要 `express.json()` 中间件 + Zod 校验：
```javascript
const { z } = require('zod')
const schema = z.object({ title: z.string().min(1) })
app.post("/articles", (req, res) => {
    const result = schema.safeParse(req.body)
    if (!result.success) return res.status(422).json(result.error)
})
```

FastAPI 直接用 Pydantic：
```python
from pydantic import BaseModel, Field

class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str
    tags: list[str] = []

@app.post("/articles")
def create_article(article: ArticleCreate):
    return {"id": 1, **article.model_dump()}
```

自动完成的：
1. 解析 JSON body → ArticleCreate 实例
2. 校验每个字段
3. 校验失败 → 自动返回 422 + 详细错误信息
4. 校验通过 → 类型安全的 Pydantic 对象

## 4. 响应模型 — response_model

用 `response_model` 控制返回的字段，防止泄露敏感数据：

```python
class ArticleDetail(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    author: str = "anonymous"

fake_db = {
    1: {
        "id": 1, "title": "...", "content": "...", "tags": ["AI"],
        "author": "张三", "password_hash": "secret123",
    }
}

@app.get("/articles/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int):
    return fake_db[article_id]  # password_hash 被自动过滤
```

Express 需要手动解构排除：`const { password_hash, ...safe } = article`。FastAPI 自动按模型定义过滤。

## 5. RAG 接口 — 把 RAG 变成 API

两个端点：
- `POST /index` — 索引文档（分块 + 存入向量库）
- `POST /ask` — 提问（检索 + AI 回答）

```python
class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)

class AskResponse(BaseModel):
    answer: str
    sources: list[dict]
    question: str

@app.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    # Step 1: 检索
    results = collection.query(query_texts=[req.question], n_results=req.top_k)

    # Step 2: 拼接上下文
    context = "\n\n---\n\n".join(results["documents"][0])

    # Step 3: 构造 RAG prompt → 调 LLM
    rag_prompt = f"根据以下文档回答问题...\n\n{context}\n\n问题：{req.question}"
    answer = ask(client, MODEL, rag_prompt)

    return AskResponse(answer=answer, sources=[...], question=req.question)
```

JS 前端调用：
```javascript
const { answer, sources } = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: "什么是 RAG？", top_k: 3 })
}).then(r => r.json())
```

## 6. SSE 流式输出 — 打字机效果

ChatGPT 那种逐字输出就是 SSE（Server-Sent Events）。

### SSE vs WebSocket

| | SSE | WebSocket |
|---|---|---|
| 方向 | 单向（服务器→客户端） | 双向 |
| 协议 | HTTP | 独立协议（需要握手） |
| 适用场景 | AI 流式输出、通知推送 | 聊天室、游戏 |
| 复杂度 | 低 | 高 |

### FastAPI 实现

方法 1 — StreamingResponse（内置）：
```python
from fastapi.responses import StreamingResponse

@app.post("/stream")
async def stream():
    async def generate():
        for chunk in ["RAG ", "是检索", "增强生成"]:
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.3)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

方法 2 — sse-starlette（更标准）：
```python
from sse_starlette.sse import EventSourceResponse

@app.post("/stream/sse")
async def stream_sse():
    async def generate():
        for part in ["第一段", "第二段"]:
            yield {"event": "message", "data": part}
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(generate())
```

### 前端消费 SSE

方法 1 — EventSource（只支持 GET）：
```javascript
const source = new EventSource("/stream")
source.onmessage = (e) => {
    if (e.data === "[DONE]") { source.close(); return }
    output.textContent += e.data
}
```

方法 2 — fetch + ReadableStream（支持 POST，推荐）：
```javascript
const response = await fetch("/ask", { method: "POST", body: JSON.stringify({ question }) })
const reader = response.body.getReader()
const decoder = new TextDecoder()
while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const text = decoder.decode(value)
    // 解析 SSE 格式，追加到 UI
}
```

## 7. CORS + 静态文件

### CORS 中间件

Express：`app.use(cors({ origin: "http://localhost:3000" }))`
FastAPI：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 静态文件

Express：`app.use("/static", express.static("static"))`
FastAPI：
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 错误处理

Express：`app.use((err, req, res, next) => { ... })`
FastAPI：
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
```

## 总结速查

```
Express → FastAPI 速查：
  app.get('/path', handler)     → @app.get('/path')
  req.params.id                 → 函数参数 (path param)
  req.query.page                → 函数参数 + 默认值 (query param)
  req.body + Zod               → Pydantic Model 参数
  res.json({...})               → return {...}
  res.status(201).json(...)     → JSONResponse(status_code=201, ...)
  app.use(cors())               → app.add_middleware(CORSMiddleware, ...)
  app.use(express.static(...))  → app.mount('/static', StaticFiles(...))
  res.write() / SSE             → StreamingResponse / EventSourceResponse
```

启动命令：
```bash
uvicorn week3-rag-and-fastapi.04_fastapi_basics:app --reload
# 访问 http://localhost:8000/docs 查看自动生成的 API 文档
```

## 推荐资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SSE 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI vs Express 详细对比](https://fastapi.tiangolo.com/async/)
