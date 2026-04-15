# ===========================================
# Day 3: MCP — Model Context Protocol
# ===========================================
# MCP = 模型上下文协议 — AI 工具的"USB 接口"
#
# 类比：
# 以前：每接一个工具都要写适配代码（就像每个设备一根线）
# MCP：  统一协议，工具即插即用（就像 USB，插上就能用）
#
# 前端类比：
# Function Calling = 手动 import 并调用函数
# MCP = npm 包管理 + 自动发现 — install 后自动可用
# ===========================================

# 安装：
# pip install mcp httpx

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")

from utils import get_client, ask

client, MODEL = get_client(Path(__file__).parent / ".env")


# ===========================================
# 1. MCP 的定位和价值
# ===========================================
# MCP 是 Anthropic 提出的开放协议
# 目标：让 AI 应用能"即插即用"地接入外部工具
#
# 没有 MCP 之前：
#   App A 要接搜索 → 写搜索适配代码
#   App B 要接搜索 → 再写一遍适配代码
#   App A 要接日历 → 又写一遍...
#
# 有了 MCP 之后：
#   搜索工具实现 MCP Server → 所有 App 直接连
#   日历工具实现 MCP Server → 所有 App 直接连
#
# JS 类比：
# 没有 MCP = 每个组件手动 fetch 不同 API
# 有了 MCP = 浏览器 Extension API，写一次到处用
#
# 架构图：
# ┌──────────┐     MCP 协议     ┌──────────────┐
# │ AI 应用   │ ←───────────→ │ MCP Server    │
# │ (Client)  │               │ (提供工具)     │
# └──────────┘               └──────────────┘
#                             可以是：搜索、文件系统、数据库...

print("=== Section 1: MCP 的定位 ===")
print("MCP = AI 工具的统一接口协议")
print("Client (AI App) ←→ Server (工具提供方)")
print()


# ===========================================
# 2. MCP vs Function Calling 对比
# ===========================================
# 两者都能让 AI 调用工具，但方式不同
#
# Function Calling：
#   工具定义写在 prompt 或代码里
#   改工具 → 改代码 → 重新部署
#
# MCP：
#   工具由 Server 动态提供
#   改工具 → 只改 Server → Client 自动发现新工具

print("=== Section 2: MCP vs Function Calling ===")
print("┌─────────────┬──────────────────┬──────────────────┐")
print("│    维度      │ Function Calling  │       MCP        │")
print("├─────────────┼──────────────────┼──────────────────┤")
print("│ 工具定义    │ 硬编码在代码里    │ Server 动态提供   │")
print("│ 修改工具    │ 改代码+重新部署   │ 只改 Server       │")
print("│ 工具来源    │ 本地定义          │ 远程 Server      │")
print("│ 发现机制    │ 无（写死的）      │ 自动发现          │")
print("│ 复用性      │ 低（每个 App 写） │ 高（Server 共享） │")
print("│ JS 类比     │ 手动 import       │ npm install      │")
print("└─────────────┴──────────────────┴──────────────────┘")
print()


# ===========================================
# 3. MCP 协议结构（模拟演示）
# ===========================================
# MCP 通信流程：
# 1. Client 连接 Server
# 2. Client 调用 tools/list → Server 返回可用工具列表
# 3. Client 调用 tools/call → Server 执行工具并返回结果
#
# JS 类比：
# // 连接
# const mcp = new MCPClient('http://localhost:3000');
# // 发现工具
# const tools = await mcp.listTools();
# // 调用工具
# const result = await mcp.callTool('get_time', {});

# 模拟 MCP Server（用 Python class 模拟协议流程）
class MockMCPServer:
    """
    模拟 MCP Server

    实际 MCP Server 是一个独立进程，通过 stdio 或 HTTP 通信
    这里用 class 模拟协议交互，帮助理解流程
    """

    def __init__(self, name):
        self.name = name
        self._tools = {}

    def register_tool(self, name, description, fn, parameters=None):
        """注册工具（Server 端）"""
        self._tools[name] = {
            "name": name,
            "description": description,
            "fn": fn,
            "parameters": parameters or {},
        }

    def list_tools(self):
        """
        tools/list — 返回可用工具列表

        JS 类比：GET /api/tools → [{name, description, parameters}]
        """
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["parameters"],
            }
            for t in self._tools.values()
        ]

    def call_tool(self, name, arguments=None):
        """
        tools/call — 调用指定工具

        JS 类比：POST /api/tools/:name { arguments }
        """
        if name not in self._tools:
            return {"error": f"Tool '{name}' not found"}

        try:
            result = self._tools[name]["fn"](arguments or {})
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            return {"error": str(e)}


# 模拟 MCP Client
class MockMCPClient:
    """
    模拟 MCP Client

    实际 MCP Client 会通过 stdio 或 HTTP 连接 Server
    这里直接引用 Server 对象来模拟
    """

    def __init__(self, server):
        self.server = server
        self.available_tools = []

    def connect(self):
        """连接 Server 并发现工具"""
        self.available_tools = self.server.list_tools()
        print(f"  ✅ 已连接 Server: {self.server.name}")
        print(f"  📋 发现 {len(self.available_tools)} 个工具:")
        for tool in self.available_tools:
            print(f"     - {tool['name']}: {tool['description']}")

    def call(self, tool_name, arguments=None):
        """调用工具"""
        result = self.server.call_tool(tool_name, arguments)
        return result


# 创建 Server 并注册工具
server = MockMCPServer("demo-tools")

server.register_tool(
    name="get_time",
    description="获取当前时间",
    fn=lambda args: datetime.now().strftime(args.get("format", "%Y-%m-%d %H:%M:%S")),
    parameters={"type": "object", "properties": {"format": {"type": "string"}}},
)

server.register_tool(
    name="random_number",
    description="生成随机数",
    fn=lambda args: __import__("random").randint(
        args.get("min", 1), args.get("max", 100)
    ),
    parameters={
        "type": "object",
        "properties": {
            "min": {"type": "integer"},
            "max": {"type": "integer"},
        },
    },
)

server.register_tool(
    name="word_count",
    description="统计文本字数",
    fn=lambda args: len(args.get("text", "")),
    parameters={"type": "object", "properties": {"text": {"type": "string"}}},
)

# 创建 Client 并连接
print("=== Section 3: MCP 协议模拟 ===")
mcp_client = MockMCPClient(server)
mcp_client.connect()

# 调用工具
print("\n调用 get_time:")
result = mcp_client.call("get_time", {"format": "%Y年%m月%d日"})
print(f"  结果: {result}")

print("\n调用 random_number:")
result = mcp_client.call("random_number", {"min": 1, "max": 10})
print(f"  结果: {result}")

print("\n调用 word_count:")
result = mcp_client.call("word_count", {"text": "Hello MCP World"})
print(f"  结果: {result}")


# ===========================================
# 4. 写最小 MCP Server（可选实战）
# ===========================================
# 用 mcp SDK 写真实 MCP Server
#
# 注意：需要 pip install mcp
# 如果安装失败，看上面的模拟版本理解即可
#
# MCP Server 就像一个 Express 服务器：
# - Express 暴露 HTTP 路由
# - MCP Server 暴露工具

# --- 以下代码需要 mcp SDK，如果没装就跳过 ---

# try:
#     from mcp.server import Server
#     from mcp.types import Tool, TextContent
#     import mcp.server.stdio
#
#     # 创建 MCP Server
#     mcp_server = Server("my-tools")
#
#     @mcp_server.list_tools()
#     async def list_tools():
#         """返回工具列表"""
#         return [
#             Tool(
#                 name="get_time",
#                 description="获取当前时间",
#                 inputSchema={
#                     "type": "object",
#                     "properties": {
#                         "format": {"type": "string", "description": "时间格式"}
#                     },
#                 },
#             ),
#             Tool(
#                 name="calculator",
#                 description="计算数学表达式",
#                 inputSchema={
#                     "type": "object",
#                     "properties": {
#                         "expression": {"type": "string", "description": "数学表达式"}
#                     },
#                     "required": ["expression"],
#                 },
#             ),
#         ]
#
#     @mcp_server.call_tool()
#     async def call_tool(name, arguments):
#         """执行工具"""
#         if name == "get_time":
#             fmt = arguments.get("format", "%Y-%m-%d %H:%M:%S")
#             return [TextContent(type="text", text=datetime.now().strftime(fmt))]
#         elif name == "calculator":
#             expr = arguments["expression"]
#             result = eval(expr)
#             return [TextContent(type="text", text=str(result))]
#         else:
#             raise ValueError(f"Unknown tool: {name}")
#
#     # 启动 Server（通过 stdio 通信）
#     # async def main():
#     #     async with mcp.server.stdio.stdio_server() as (read, write):
#     #         await mcp_server.run(read, write)
#     # asyncio.run(main())
#
#     print("\n=== Section 4: 真实 MCP Server ===")
#     print("MCP SDK 已安装，Server 代码已就绪")
#     print("启动方式: python 03_mcp.py (作为 MCP Server)")
#
# except ImportError:
#     print("\n=== Section 4: MCP SDK 未安装 ===")
#     print("pip install mcp 后可运行真实 MCP Server")
#     print("上面的模拟版本已经覆盖了核心概念")


# ===========================================
# 5. MCP 工具集成到 Agent
# ===========================================
# 把 MCP 发现的工具转换成 Agent 可用的格式
# 流程：
# 1. MCP Client 连接 Server → 获取工具列表
# 2. 把工具描述转成 LLM 能理解的文本
# 3. Agent 根据 LLM 输出调用对应工具
#
# JS 类比：
# const mcpTools = await mcp.listTools();
# const toolsForLLM = mcpTools.map(t => ({
#   name: t.name,
#   description: t.description,
# }));
# agent.setTools(toolsForLLM, mcp.callTool);

def mcp_tools_to_agent_format(mcp_client):
    """
    把 MCP 工具转换成 Agent 工具注册表

    参数:
        mcp_client: MockMCPClient 实例

    返回:
        Agent 可用的 tools dict
    """
    tools = {}
    for tool in mcp_client.available_tools:
        name = tool["name"]
        tools[name] = {
            "description": tool["description"],
            "fn": lambda args_str, n=name: mcp_client.call(n, _parse_args(args_str)),
        }
    return tools


def _parse_args(args_str):
    """尝试把字符串参数解析成 dict"""
    try:
        return json.loads(args_str)
    except (json.JSONDecodeError, TypeError):
        return {"text": str(args_str)}


# print("\n=== Section 5: MCP + Agent 集成 ===")
#
# # 把 MCP 工具转成 Agent 格式
# agent_tools = mcp_tools_to_agent_format(mcp_client)
# print(f"Agent 可用工具: {list(agent_tools.keys())}")
#
# # 用 Day 1 的 SimpleAgent 类
# # （这里简化演示，直接调用）
# for name, tool in agent_tools.items():
#     result = tool["fn"](json.dumps({"min": 1, "max": 100}) if name == "random_number" else "{}")
#     print(f"  {name}: {result}")

print("\n=== Section 5: MCP + Agent 集成 ===")
agent_tools = mcp_tools_to_agent_format(mcp_client)
print(f"已将 MCP 工具转为 Agent 格式: {list(agent_tools.keys())}")
print("可以直接传给 SimpleAgent(tools=agent_tools) 使用")
