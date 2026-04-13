# ===========================================
# Day 5: 前端对接 — 给 RAG 穿上好看的衣服
# ===========================================
# 前端工程师的优势时刻！用 HTML + CSS + JS 打造聊天界面
# FastAPI 负责 SSE 流式推送，前端负责实时渲染
#
# 类比：
# SSE = EventSource（浏览器原生 API）
# FastAPI SSE = Express + res.write() 的 Python 版
#
# 前端类比：
# 这个文件 = Next.js API Route + 前端页面 的 all-in-one 版本
# EventSourceResponse = res.write() + Transfer-Encoding: chunked
# ===========================================

# 安装依赖（如果还没装）：
# pip install fastapi uvicorn sse-starlette chromadb python-dotenv

import sys
import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import chromadb


# ===========================================
# 1. 前端方案选择
# ===========================================
# 学习阶段推荐：纯 HTML + CSS + JS
# 原因：
#   - 不需要 npm / webpack / vite 等构建工具
#   - FastAPI 直接返回 HTML 字符串，一个文件搞定
#   - 前端工程师写这些就是降维打击
#
# 生产环境推荐：
#   - React/Vue + Vite，前后端分离
#   - FastAPI 只做 API 层
#   - 但学习阶段没必要搞这么复杂
#
# JS 类比：
# 现在做的事 = Express 里直接 res.send(htmlString)
# 等熟练后再上 Next.js 全家桶


# ===========================================
# 2. FastAPI 服务
# ===========================================

app = FastAPI(title="RAG Chat", description="RAG 聊天助手 — Day 5 前端对接")

# CORS — 前后端分离时需要，现在同域其实不需要，但养成好习惯
# JS 类比：跟 Express 里的 cors() 中间件一样
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 全局变量 ---
client_ai = None
MODEL = None
rag_collection = None


@app.on_event("startup")
async def startup():
    """
    应用启动时初始化 AI 客户端和向量库

    JS 类比：
    // Express
    app.listen(3000, async () => {
        await initDB();
        await loadModels();
    });
    """
    global client_ai, MODEL, rag_collection
    client_ai, MODEL = get_client(Path(__file__).parent / ".env")
    rag_collection = init_vector_store()
    print("\n[启动完成] AI 客户端和向量库已初始化")
    print("[访问] http://localhost:8000\n")


# --- GET / — 返回聊天界面 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    """
    返回聊天页面 HTML

    JS 类比：
    app.get("/", (req, res) => res.sendFile("index.html"))
    但我们直接返回字符串，不需要文件
    """
    return HTMLResponse(content=CHAT_HTML, status_code=200)


# --- POST /ask — RAG + SSE 流式回答 ---
@app.post("/ask")
async def ask_rag(request: Request):
    """
    接收用户问题，检索文档，流式返回 AI 回答

    SSE 事件格式：
    - event: token   → 每个文字片段
    - event: sources → 引用的文档来源
    - event: done    → 结束信号

    JS 类比：
    app.post("/ask", (req, res) => {
        res.setHeader("Content-Type", "text/event-stream");
        // ... 每次 res.write(`data: ${chunk}\n\n`)
    });
    """
    body = await request.json()
    question = body.get("question", "").strip()

    if not question:
        return {"error": "问题不能为空"}

    # Step 1: 检索相关文档
    search_results = search_docs(question, n_results=3)
    sources = search_results["sources"]
    context = search_results["context"]

    # Step 2: 构建 RAG prompt
    rag_prompt = f"""你是一个知识助手。根据以下参考文档回答用户的问题。
要求：
1. 只基于文档内容回答，不要编造
2. 如果文档中没有相关信息，明确说"根据现有文档无法回答这个问题"
3. 回答要简洁清晰
4. 适当引用文档中的原文

参考文档：
{context}

用户问题：{question}"""

    # Step 3: 流式生成回答（SSE）
    async def event_generator():
        """
        SSE 事件生成器

        yield 的格式：
        {"event": "事件名", "data": "数据内容"}

        浏览器端 EventSource 会收到：
        event: token
        data: 你好

        """
        try:
            # 调用 AI 流式 API
            stream = client_ai.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": rag_prompt}],
                stream=True,
            )

            for event in stream:
                # content_block_delta 事件包含实际文本
                if event.type == "content_block_delta":
                    text = event.delta.text
                    if text:
                        yield {
                            "event": "token",
                            "data": json.dumps({"text": text}, ensure_ascii=False),
                        }
                        # 小延迟让前端有时间渲染（可选）
                        await asyncio.sleep(0.01)

            # 发送引用来源
            yield {
                "event": "sources",
                "data": json.dumps(sources, ensure_ascii=False),
            }

            # 发送结束信号
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"}),
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


# ===========================================
# 3. HTML 模板 — 聊天界面
# ===========================================
# 纯 HTML + CSS + JS，不需要任何构建工具
# CSS 用变量系统（CSS Custom Properties）
# JS 用原生 EventSource 接收 SSE

CHAT_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Chat - AI 知识助手</title>
    <style>
        /* ===== CSS 变量 — 方便统一调整主题 ===== */
        :root {
            --bg-primary: #f7f7f8;
            --bg-secondary: #ffffff;
            --bg-user-msg: #2563eb;
            --bg-ai-msg: #ffffff;
            --text-primary: #1a1a2e;
            --text-secondary: #6b7280;
            --text-user-msg: #ffffff;
            --text-ai-msg: #1a1a2e;
            --border-color: #e5e7eb;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            --transition: all 0.2s ease;
            --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
            --font-mono: "SF Mono", "Fira Code", "Cascadia Code", Consolas, monospace;
            --max-width: 800px;
        }

        /* ===== Reset & Base ===== */
        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html { height: 100%; }

        body {
            font-family: var(--font-sans);
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100%;
            display: flex;
            flex-direction: column;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        /* ===== Header ===== */
        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            box-shadow: var(--shadow-sm);
            position: relative;
            z-index: 10;
        }

        .header-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--accent), #7c3aed);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            font-weight: 700;
        }

        .header h1 {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .header .subtitle {
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 400;
        }

        /* ===== Chat Container ===== */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 24px 16px;
            scroll-behavior: smooth;
        }

        .chat-messages {
            max-width: var(--max-width);
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* ===== Welcome ===== */
        .welcome {
            text-align: center;
            padding: 48px 24px;
            animation: fadeInUp 0.5s ease;
        }

        .welcome-icon {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, var(--accent), #7c3aed);
            border-radius: var(--radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 28px;
            color: white;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
        }

        .welcome h2 {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .welcome p {
            color: var(--text-secondary);
            font-size: 15px;
            max-width: 420px;
            margin: 0 auto 24px;
        }

        .quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }

        .quick-btn {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-full);
            padding: 8px 16px;
            font-size: 13px;
            color: var(--text-primary);
            cursor: pointer;
            transition: var(--transition);
            font-family: var(--font-sans);
        }

        .quick-btn:hover {
            border-color: var(--accent);
            color: var(--accent);
            box-shadow: var(--shadow-sm);
        }

        /* ===== Message Bubbles ===== */
        .message {
            display: flex;
            gap: 12px;
            animation: fadeInUp 0.3s ease;
            max-width: 85%;
        }

        .message.user {
            flex-direction: row-reverse;
            align-self: flex-end;
        }

        .message.ai {
            align-self: flex-start;
        }

        .avatar {
            width: 34px;
            height: 34px;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            flex-shrink: 0;
            margin-top: 2px;
        }

        .message.user .avatar {
            background: var(--bg-user-msg);
            color: var(--text-user-msg);
        }

        .message.ai .avatar {
            background: linear-gradient(135deg, #f0f4ff, #e8ecf8);
            color: var(--accent);
        }

        .bubble {
            padding: 12px 16px;
            border-radius: var(--radius-md);
            font-size: 14.5px;
            line-height: 1.7;
            position: relative;
            word-break: break-word;
        }

        .message.user .bubble {
            background: var(--bg-user-msg);
            color: var(--text-user-msg);
            border-bottom-right-radius: 4px;
        }

        .message.ai .bubble {
            background: var(--bg-ai-msg);
            color: var(--text-ai-msg);
            border: 1px solid var(--border-color);
            border-bottom-left-radius: 4px;
            box-shadow: var(--shadow-sm);
        }

        .message.ai .bubble p { margin-bottom: 8px; }
        .message.ai .bubble p:last-child { margin-bottom: 0; }

        .message.ai .bubble code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: var(--font-mono);
            font-size: 13px;
        }

        .message.ai .bubble pre {
            background: #1e1e2e;
            color: #cdd6f4;
            padding: 14px 16px;
            border-radius: var(--radius-sm);
            overflow-x: auto;
            margin: 10px 0;
            font-size: 13px;
            line-height: 1.5;
        }

        .message.ai .bubble pre code {
            background: none;
            padding: 0;
            color: inherit;
        }

        /* ===== Typing Indicator ===== */
        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 4px 0;
        }

        .typing-indicator span {
            width: 7px;
            height: 7px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
            opacity: 0.5;
        }

        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        /* ===== Sources (Collapsible) ===== */
        .sources {
            margin-top: 12px;
            border-top: 1px solid var(--border-color);
            padding-top: 10px;
        }

        .sources-toggle {
            background: none;
            border: none;
            color: var(--accent);
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: var(--font-sans);
            padding: 4px 0;
            transition: var(--transition);
        }

        .sources-toggle:hover { opacity: 0.8; }

        .sources-toggle .arrow {
            display: inline-block;
            transition: transform 0.2s ease;
            font-size: 10px;
        }

        .sources-toggle.open .arrow { transform: rotate(90deg); }

        .sources-list {
            display: none;
            margin-top: 8px;
            padding-left: 0;
            list-style: none;
        }

        .sources-list.visible { display: block; }

        .sources-list li {
            font-size: 13px;
            color: var(--text-secondary);
            padding: 6px 10px;
            background: #f9fafb;
            border-radius: 6px;
            margin-bottom: 4px;
            border-left: 3px solid var(--accent);
        }

        .sources-list li .source-file {
            font-weight: 500;
            color: var(--text-primary);
        }

        .sources-list li .source-preview {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 2px;
            display: block;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* ===== Input Area ===== */
        .input-area {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-color);
            padding: 16px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.03);
        }

        .input-wrapper {
            max-width: var(--max-width);
            margin: 0 auto;
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .input-box {
            flex: 1;
            position: relative;
        }

        .input-box textarea {
            width: 100%;
            padding: 12px 16px;
            border: 1.5px solid var(--border-color);
            border-radius: var(--radius-md);
            font-size: 14.5px;
            font-family: var(--font-sans);
            line-height: 1.5;
            resize: none;
            outline: none;
            transition: var(--transition);
            min-height: 46px;
            max-height: 140px;
            background: var(--bg-primary);
            color: var(--text-primary);
        }

        .input-box textarea:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .input-box textarea::placeholder { color: #9ca3af; }

        .send-btn {
            width: 46px;
            height: 46px;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
            flex-shrink: 0;
        }

        .send-btn:hover:not(:disabled) {
            background: var(--accent-hover);
            transform: scale(1.05);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .send-btn svg {
            width: 20px;
            height: 20px;
        }

        .input-hint {
            text-align: center;
            font-size: 12px;
            color: #9ca3af;
            margin-top: 8px;
        }

        /* ===== Error Toast ===== */
        .error-toast {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: #fee2e2;
            color: #dc2626;
            padding: 12px 24px;
            border-radius: var(--radius-md);
            font-size: 14px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            transition: transform 0.3s ease;
            border: 1px solid #fecaca;
        }

        .error-toast.show {
            transform: translateX(-50%) translateY(0);
        }

        /* ===== Animations ===== */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0.6); }
            40% { transform: scale(1); }
        }

        /* ===== Scrollbar ===== */
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }

        .chat-container::-webkit-scrollbar-track {
            background: transparent;
        }

        .chat-container::-webkit-scrollbar-thumb {
            background: #d1d5db;
            border-radius: 3px;
        }

        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #9ca3af;
        }

        /* ===== Responsive ===== */
        @media (max-width: 640px) {
            .header { padding: 12px 16px; }
            .chat-container { padding: 16px 12px; }
            .message { max-width: 92%; }
            .quick-questions { flex-direction: column; align-items: center; }
        }
    </style>
</head>
<body>

<!-- Header -->
<div class="header">
    <div class="header-icon">R</div>
    <div>
        <h1>RAG Chat <span class="subtitle">/ AI 知识助手</span></h1>
    </div>
</div>

<!-- Chat Messages -->
<div class="chat-container" id="chatContainer">
    <div class="chat-messages" id="chatMessages">
        <!-- Welcome Screen -->
        <div class="welcome" id="welcome">
            <div class="welcome-icon">?</div>
            <h2>Hi, 有什么想了解的？</h2>
            <p>我会从知识库中检索相关文档，基于真实内容为你解答，而不是凭空编造。</p>
            <div class="quick-questions">
                <button class="quick-btn" onclick="askQuestion('React 有哪些常用 Hooks？')">React 常用 Hooks</button>
                <button class="quick-btn" onclick="askQuestion('Python 列表推导式怎么用？')">Python 列表推导式</button>
                <button class="quick-btn" onclick="askQuestion('RESTful API 设计规范是什么？')">RESTful API 设计</button>
                <button class="quick-btn" onclick="askQuestion('如何做前端性能优化？')">前端性能优化</button>
            </div>
        </div>
    </div>
</div>

<!-- Error Toast -->
<div class="error-toast" id="errorToast"></div>

<!-- Input Area -->
<div class="input-area">
    <div class="input-wrapper">
        <div class="input-box">
            <textarea
                id="userInput"
                placeholder="输入你的问题..."
                rows="1"
                onkeydown="handleKeyDown(event)"
                oninput="autoResize(this)"
            ></textarea>
        </div>
        <button class="send-btn" id="sendBtn" onclick="sendMessage()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
        </button>
    </div>
    <div class="input-hint">Enter 发送 / Shift+Enter 换行</div>
</div>

<script>
// ===========================================
// 前端 JS — 原生实现，无依赖
// ===========================================
// 对前端工程师来说这些代码很基础
// 重点关注 SSE 部分（EventSource / fetch + ReadableStream）

const chatMessages = document.getElementById('chatMessages');
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const welcome = document.getElementById('welcome');
const errorToast = document.getElementById('errorToast');

let isStreaming = false;
let currentController = null;  // AbortController，用于取消请求

// --- 自动调整 textarea 高度 ---
function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

// --- 键盘事件 ---
function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// --- 快捷问题 ---
function askQuestion(text) {
    userInput.value = text;
    sendMessage();
}

// --- 滚动到底部 ---
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// --- 显示错误 ---
function showError(msg) {
    errorToast.textContent = msg;
    errorToast.classList.add('show');
    setTimeout(() => errorToast.classList.remove('show'), 3000);
}

// --- 简单 Markdown 渲染 ---
// 生产环境用 marked.js，学习阶段手写一个基础版
function renderMarkdown(text) {
    return text
        // 代码块
        .replace(/```(\\w*)\\n([\\s\\S]*?)```/g, '<pre><code>$2</code></pre>')
        // 行内代码
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // 加粗
        .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
        // 斜体
        .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
        // 换行
        .replace(/\\n/g, '<br>');
}

// --- 添加消息到界面 ---
function addMessage(role, content) {
    // 隐藏欢迎页
    if (welcome) welcome.style.display = 'none';

    const div = document.createElement('div');
    div.className = `message ${role}`;

    const avatar = role === 'user' ? 'U' : 'AI';

    div.innerHTML = `
        <div class="avatar">${avatar}</div>
        <div class="bubble">${role === 'user' ? escapeHtml(content) : content}</div>
    `;

    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

// --- 防 XSS ---
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// --- 添加 AI 消息（流式，返回 bubble 元素用于追加内容）---
function addStreamingMessage() {
    if (welcome) welcome.style.display = 'none';

    const div = document.createElement('div');
    div.className = 'message ai';
    div.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;

    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

// --- 添加引用来源 ---
function addSources(msgDiv, sources) {
    if (!sources || sources.length === 0) return;

    const bubble = msgDiv.querySelector('.bubble');
    const sourcesHtml = `
        <div class="sources">
            <button class="sources-toggle" onclick="toggleSources(this)">
                <span class="arrow">&#9654;</span>
                引用来源 (${sources.length})
            </button>
            <ul class="sources-list">
                ${sources.map(s => `
                    <li>
                        <span class="source-file">${escapeHtml(s.source)}</span>
                        <span class="source-preview">${escapeHtml(s.preview)}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
    bubble.insertAdjacentHTML('beforeend', sourcesHtml);
}

// --- 展开/收起来源 ---
function toggleSources(btn) {
    btn.classList.toggle('open');
    const list = btn.nextElementSibling;
    list.classList.toggle('visible');
}

// ===========================================
// 核心：发送消息 + SSE 流式接收
// ===========================================
// 这里用 fetch + ReadableStream 而不是 EventSource
// 原因：EventSource 只支持 GET，我们需要 POST 发送请求体
//
// JS 知识点：
// - fetch 返回 Response，body 是 ReadableStream
// - getReader() 获取流的读取器
// - TextDecoder 把 Uint8Array 解码成字符串
// - SSE 格式：每个事件以 \\n\\n 分隔

async function sendMessage() {
    const question = userInput.value.trim();
    if (!question || isStreaming) return;

    // UI 状态
    isStreaming = true;
    sendBtn.disabled = true;
    userInput.value = '';
    userInput.style.height = 'auto';

    // 添加用户消息
    addMessage('user', question);

    // 添加 AI 消息占位（含 loading 动画）
    const aiMsg = addStreamingMessage();
    const bubble = aiMsg.querySelector('.bubble');

    // AbortController — 用于取消请求
    currentController = new AbortController();

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
            signal: currentController.signal,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        // 读取 SSE 流
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        let buffer = '';
        let typingRemoved = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // SSE 格式解析：event: xxx\\ndata: xxx\\n\\n
            const lines = buffer.split('\\n');
            buffer = '';  // 重置 buffer

            let currentEvent = '';

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];

                if (line.startsWith('event:')) {
                    currentEvent = line.slice(6).trim();
                } else if (line.startsWith('data:')) {
                    const data = line.slice(5).trim();

                    try {
                        const parsed = JSON.parse(data);

                        if (currentEvent === 'token') {
                            // 移除 loading 动画
                            if (!typingRemoved) {
                                bubble.innerHTML = '';
                                typingRemoved = true;
                            }
                            fullText += parsed.text;
                            bubble.innerHTML = renderMarkdown(fullText);
                            scrollToBottom();

                        } else if (currentEvent === 'sources') {
                            addSources(aiMsg, parsed);

                        } else if (currentEvent === 'error') {
                            showError(parsed.message || '生成出错');

                        } else if (currentEvent === 'done') {
                            // 流式结束
                        }
                    } catch (e) {
                        // JSON 解析失败，可能是不完整的数据，放回 buffer
                        if (i === lines.length - 1) {
                            buffer = line;
                        }
                    }

                    currentEvent = '';  // 重置事件类型

                } else if (line.trim() === '' ) {
                    // 空行 = 事件分隔符，不处理
                } else {
                    // 不完整的行，可能需要放回 buffer
                    if (i === lines.length - 1 && line.length > 0) {
                        buffer = line;
                    }
                }
            }
        }

        // 如果从未收到 token（可能后端出错）
        if (!typingRemoved) {
            bubble.innerHTML = '<span style="color:#9ca3af">未收到回复，请重试</span>';
        }

    } catch (err) {
        if (err.name === 'AbortError') {
            bubble.innerHTML += '<br><span style="color:#9ca3af">[已取消]</span>';
        } else {
            bubble.innerHTML = `<span style="color:#dc2626">请求失败: ${escapeHtml(err.message)}</span>`;
            showError('请求失败，请检查后端服务是否运行');
        }
    } finally {
        isStreaming = false;
        sendBtn.disabled = false;
        currentController = null;
        userInput.focus();
    }
}
</script>

</body>
</html>"""


# ===========================================
# 4. RAG 后端逻辑
# ===========================================
# 初始化向量库 + 索引文档 + 检索函数

def init_vector_store():
    """
    初始化 ChromaDB 并索引 sample_docs 目录下的文档

    流程：
    1. 创建内存模式的 Chroma 客户端
    2. 读取所有 .md 文件
    3. 按段落分块
    4. 存入向量库

    JS 类比：
    async function initDB() {
        const db = new Database();
        const docs = fs.readdirSync("./docs");
        docs.forEach(doc => db.insert(chunk(doc)));
        return db;
    }
    """
    chroma = chromadb.Client()

    # 如果 collection 已存在则删除（开发阶段方便重启）
    try:
        chroma.delete_collection("rag_chat")
    except Exception:
        pass

    collection = chroma.create_collection(
        name="rag_chat",
        metadata={"hnsw:space": "cosine"},
    )

    # 读取 sample_docs
    doc_dir = Path(__file__).parent / "sample_docs"
    all_chunks = []
    all_ids = []
    all_metadata = []

    for doc_path in doc_dir.glob("*.md"):
        text = doc_path.read_text(encoding="utf-8")
        # 按段落分块，过滤太短的段落
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and len(p.strip()) > 20]

        for i, para in enumerate(paragraphs):
            chunk_id = f"{doc_path.stem}_{i}"
            all_chunks.append(para)
            all_ids.append(chunk_id)
            all_metadata.append({
                "source": doc_path.name,
                "preview": para[:80],
            })

    if all_chunks:
        collection.add(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadata,
        )

    print(f"[向量库] 已索引 {len(all_chunks)} 个文档块，来自 {len(list(doc_dir.glob('*.md')))} 个文件")
    return collection


def search_docs(question: str, n_results: int = 3) -> dict:
    """
    在向量库中检索与问题相关的文档

    参数:
        question: 用户问题
        n_results: 返回结果数量

    返回:
        {
            "context": "拼接后的上下文文本",
            "sources": [{"source": "文件名", "preview": "预览"}]
        }

    JS 类比：
    async function search(query) {
        const results = await vectorDB.query(query, { limit: 3 });
        return {
            context: results.map(r => r.text).join("\\n---\\n"),
            sources: results.map(r => ({ source: r.metadata.source })),
        };
    }
    """
    results = rag_collection.query(
        query_texts=[question],
        n_results=n_results,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n---\n\n".join(documents)
    sources = [
        {"source": meta["source"], "preview": meta.get("preview", "")}
        for meta in metadatas
    ]

    return {"context": context, "sources": sources}


# ===========================================
# 5. 启动说明
# ===========================================
# 方式 1（推荐）: 直接运行
#   python week3-rag-and-fastapi/05_frontend.py
#
# 方式 2: 用 uvicorn 运行（支持热重载）
#   cd week3-rag-and-fastapi
#   uvicorn 05_frontend:app --reload --port 8000
#
# 然后打开浏览器访问: http://localhost:8000
#
# 注意：
# - 确保 sample_docs/ 目录下有 .md 文件
# - 确保 .env 文件配置了 API Key
# - 第一次运行会下载 embedding 模型（约 80MB）

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("05_frontend:app", host="0.0.0.0", port=8000, reload=True)
