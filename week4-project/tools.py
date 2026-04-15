# ===========================================
# tools.py — AI Workflow Assistant 工具定义
# ===========================================
# 定义 Agent 可以调用的工具
# 每个工具：name, description, execute(input)
# ===========================================

import math
import json
from datetime import datetime
from pathlib import Path


# --- 工具 1: 搜索（模拟） ---

def web_search(query):
    """
    模拟网络搜索

    实际项目中接 Bing/Google/Tavily API
    """
    mock_data = {
        "python": "Python 3.12 是最新稳定版本。Python 是一种通用编程语言，广泛用于 AI、数据科学、Web 开发等领域。",
        "fastapi": "FastAPI 是一个现代化的高性能 Python Web 框架，基于标准 Python 类型提示构建 API，性能媲美 Node.js 和 Go。",
        "react": "React 18 是最新主要版本，引入了并发特性（Concurrent Features）、自动批处理和 Suspense 改进。",
        "docker": "Docker 是一个开源的容器化平台，让开发者可以将应用程序打包到容器中，确保在任何环境下一致运行。",
        "langgraph": "LangGraph 是 LangChain 团队开发的 Agent 编排框架，用图结构（State/Node/Edge）来构建可控的 AI 工作流。",
        "rag": "RAG（检索增强生成）是一种让 AI 先检索相关文档再回答的技术，解决大模型知识截止和私有数据问题。",
        "mcp": "MCP（Model Context Protocol）是 Anthropic 提出的开放协议，让 AI 应用能即插即用地接入外部工具。",
        "agent": "AI Agent 是能自主决策调用工具的智能体，核心是 plan → act → observe → repeat 循环。",
    }

    query_lower = query.lower()
    for key, value in mock_data.items():
        if key in query_lower:
            return {"status": "success", "result": value}

    return {"status": "success", "result": f"关于 '{query}' 的搜索结果：这是一个广泛使用的技术概念。"}


# --- 工具 2: 计算器 ---

def calculator(expression):
    """
    安全的数学计算器

    支持：加减乘除、括号、常用数学函数
    """
    try:
        # 安全检查
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return {"status": "error", "result": f"不支持的字符: {expression}"}

        result = eval(expression)
        return {"status": "success", "result": str(result)}
    except Exception as e:
        return {"status": "error", "result": f"计算错误: {e}"}


# --- 工具 3: 文件读取 ---

def file_reader(file_path):
    """
    读取文本文件内容

    安全限制：只能读 .md / .txt / .py 文件
    """
    path = Path(file_path)
    allowed_suffixes = {".md", ".txt", ".py", ".json"}

    if path.suffix not in allowed_suffixes:
        return {"status": "error", "result": f"不支持的文件类型: {path.suffix}"}

    if not path.exists():
        return {"status": "error", "result": f"文件不存在: {file_path}"}

    try:
        content = path.read_text(encoding="utf-8")
        # 限制长度
        if len(content) > 3000:
            content = content[:3000] + "\n...(内容截断)"
        return {"status": "success", "result": content}
    except Exception as e:
        return {"status": "error", "result": f"读取失败: {e}"}


# --- 工具 4: 文本摘要 ---

def text_summarize(text):
    """
    简单文本摘要（截取前 200 字 + 字数统计）

    实际项目中用 LLM 做摘要
    """
    char_count = len(text)
    preview = text[:200] + "..." if len(text) > 200 else text
    return {
        "status": "success",
        "result": f"[{char_count} 字] {preview}",
    }


# --- 工具 5: 获取时间 ---

def get_current_time(format_str=""):
    """获取当前时间"""
    fmt = format_str if format_str else "%Y-%m-%d %H:%M:%S"
    return {"status": "success", "result": datetime.now().strftime(fmt)}


# --- 工具注册表 ---

TOOLS = {
    "web_search": {
        "fn": web_search,
        "description": "搜索网络信息，输入搜索关键词",
    },
    "calculator": {
        "fn": calculator,
        "description": "计算数学表达式，如 2+3、100/4、(5+3)*2",
    },
    "file_reader": {
        "fn": file_reader,
        "description": "读取文本文件内容，输入文件路径",
    },
    "text_summarize": {
        "fn": text_summarize,
        "description": "生成文本摘要，输入要总结的文本",
    },
    "get_current_time": {
        "fn": get_current_time,
        "description": "获取当前时间，可选格式字符串",
    },
}


def get_tool_descriptions():
    """获取所有工具描述文本"""
    return "\n".join(f"- {name}: {info['description']}" for name, info in TOOLS.items())


def execute_tool(name, input_str):
    """
    执行工具

    参数:
        name: 工具名
        input_str: 工具输入（字符串）

    返回:
        {"tool": name, "input": input_str, "output": result, "status": "success"|"error"}
    """
    if name not in TOOLS:
        return {
            "tool": name,
            "input": input_str,
            "output": f"工具 '{name}' 不存在，可用: {list(TOOLS.keys())}",
            "status": "error",
        }

    try:
        result = TOOLS[name]["fn"](input_str)
        return {
            "tool": name,
            "input": input_str,
            "output": result.get("result", str(result)),
            "status": result.get("status", "success"),
        }
    except Exception as e:
        return {
            "tool": name,
            "input": input_str,
            "output": str(e),
            "status": "error",
        }
