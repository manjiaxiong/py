# Day 5: 前端对接 — 给 RAG 穿上好看的衣服

## 学习目标

- 理解 SSE 在前后端的完整链路
- 用纯 HTML + CSS + JS 实现聊天界面
- 实现 fetch + ReadableStream 消费 SSE 流
- 实现引用来源的折叠展示
- 完成 RAG 应用的端到端联调

## 方案选择

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 纯 HTML + JS | 零依赖、无需构建工具 | 无组件化、无状态管理 | 学习阶段 |
| React + Vite | 组件化、生态好 | 需要额外配置 | 生产环境 |
| Next.js | 全栈、SSR | 学习曲线陡 | 正式项目 |

学习阶段用纯 HTML，一个文件包含前端 + 后端。前端工程师写这些是降维打击。

## SSE 完整链路

### 后端发送（FastAPI + sse-starlette）

```python
from sse_starlette.sse import EventSourceResponse

@app.post("/ask")
async def ask_rag(request: Request):
    async def event_generator():
        # 流式生成回答
        stream = client_ai.messages.stream(model=MODEL, ...)
        for event in stream:
            if event.type == "content_block_delta":
                yield {"event": "token", "data": json.dumps({"text": event.delta.text})}

        # 发送引用来源
        yield {"event": "sources", "data": json.dumps(sources)}
        # 发送结束信号
        yield {"event": "done", "data": json.dumps({"status": "complete"})}

    return EventSourceResponse(event_generator())
```

### SSE 事件格式

SSE 协议规定：
- 每条消息以 `data: ` 开头
- 消息之间用空行（`\n\n`）分隔
- `event:` 字段指定事件类型

```
event: token
data: {"text": "RAG"}

event: token
data: {"text": " 是检索增强生成"}

event: sources
data: [{"source": "react_basics.md", "preview": "..."}]

event: done
data: {"status": "complete"}
```

### 前端接收（fetch + ReadableStream）

**为什么不用 EventSource？** EventSource 只支持 GET 请求，无法 POST 发送请求体。所以用 fetch + ReadableStream。

```javascript
async function sendMessage() {
    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = '';  // 重置 buffer

        let currentEvent = '';
        for (const line of lines) {
            if (line.startsWith('event:')) {
                currentEvent = line.slice(6).trim();
            } else if (line.startsWith('data:')) {
                const data = JSON.parse(line.slice(5).trim());

                if (currentEvent === 'token') {
                    fullText += data.text;
                    bubble.innerHTML = renderMarkdown(fullText);
                } else if (currentEvent === 'sources') {
                    addSources(msgDiv, data);
                } else if (currentEvent === 'done') {
                    // 流式结束
                }
            }
        }
    }
}
```

**JS 知识点**：
- `response.body` 是 ReadableStream
- `getReader()` 获取流的读取器（类似 AsyncIterable）
- `TextDecoder` 把 Uint8Array 解码成字符串
- `{ stream: true }` 支持跨块解码（防止多字节字符被切断）

## 聊天界面结构

```
┌──────────────────────────────────┐
│ Header: RAG Chat / AI 知识助手     │
├──────────────────────────────────┤
│                                  │
│  ┌─ Welcome ───────────────────┐  │
│  │  Hi, 有什么想了解的？          │  │
│  │  [快捷问题按钮 x4]            │  │
│  └─────────────────────────────┘  │
│                                  │
│  ┌─ User Message ────────────┐   │
│  │  React 有哪些常用 Hooks？    │   │
│  └────────────────────────────┘  │
│                                  │
│  ┌─ AI Message ──────────────┐   │
│  │  React 常用 Hooks 包括...    │   │
│  │  ▶ 引用来源 (3)             │   │
│  │    - react_basics.md        │   │
│  └────────────────────────────┘   │
│                                  │
├──────────────────────────────────┤
│ [输入框]              [发送按钮]    │
│ Enter 发送 / Shift+Enter 换行      │
└──────────────────────────────────┘
```

## 关键前端实现

### 1. 打字机效果（逐字追加）

每次收到 `token` 事件时，追加文本到 bubble 中：
```javascript
fullText += data.text;
bubble.innerHTML = renderMarkdown(fullText);
scrollToBottom();
```

### 2. 简单 Markdown 渲染

手写基础版（生产环境用 marked.js）：
```javascript
function renderMarkdown(text) {
    return text
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}
```

### 3. 引用来源折叠展示

```javascript
function addSources(msgDiv, sources) {
    const sourcesHtml = `
        <div class="sources">
            <button class="sources-toggle" onclick="toggleSources(this)">
                引用来源 (${sources.length})
            </button>
            <ul class="sources-list">
                ${sources.map(s => `
                    <li>
                        <span class="source-file">${s.source}</span>
                        <span class="source-preview">${s.preview}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
    bubble.insertAdjacentHTML('beforeend', sourcesHtml);
}
```

### 4. 防 XSS

用户输入必须转义：
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
// 用户消息用 escapeHtml，AI 消息用 renderMarkdown
```

### 5. 请求取消

用 AbortController 实现请求取消：
```javascript
let currentController = null;

// 发送新消息时取消旧请求
if (currentController) currentController.abort();
currentController = new AbortController();

const response = await fetch('/ask', {
    signal: currentController.signal,
    // ...
});
```

## CSS 主题系统

用 CSS Custom Properties（变量）统一管理主题：
```css
:root {
    --bg-primary: #f7f7f8;
    --bg-user-msg: #2563eb;
    --bg-ai-msg: #ffffff;
    --accent: #2563eb;
    --radius-md: 12px;
    --font-sans: -apple-system, BlinkMacSystemFont, "Noto Sans SC", sans-serif;
    --max-width: 800px;
}
```

修改一处变量，全局同步生效。

## 联调步骤

1. **启动后端**：`python week3-rag-and-fastapi/05_frontend.py`
2. **打开浏览器**：访问 `http://localhost:8000`
3. **测试快捷问题**：点击预设问题按钮
4. **测试自定义问题**：输入问题，观察流式输出
5. **检查引用来源**：展开来源列表，确认文件名和预览正确
6. **测试错误场景**：输入空问题、断开网络等

## 生产环境升级路径

当前方案 → 生产环境：

| 当前 | 升级后 |
|------|--------|
| 纯 HTML 单文件 | React + Vite 前后端分离 |
| 内嵌 HTML 字符串 | templates/index.html 独立文件 |
| 内存模式 Chroma | 持久化 Chroma 或 Pinecone |
| 单用户 | 多用户 + 对话历史 |
| 手动 Markdown | marked.js / react-markdown |

## 总结

```
前端技术栈回顾：
  fetch + POST        → 发送问题
  ReadableStream       → 接收 SSE 流
  TextDecoder          → 二进制转字符串
  innerHTML +=         → 逐字追加（打字机效果）
  insertAdjacentHTML   → 追加引用来源
  AbortController      → 取消请求
  CSS Variables        → 主题管理
  CSS Flexbox          → 布局
```

启动命令：
```bash
python week3-rag-and-fastapi/05_frontend.py
# 或
uvicorn 05_frontend:app --reload --port 8000
```

## 推荐资源

- [SSE 规范 MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [ReadableStream API](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API)
- [AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
