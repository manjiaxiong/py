# ===========================================
# 练习 3：MCP（对应 Day 3）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 03_mcp.py / 03_mcp.md
# ===========================================

import json
from datetime import datetime
import random


# --- 题目 1: MCP 概念理解 ---

# 选择题答案：

# 1.1 MCP 的全称是什么？
# 答案：Model Context Protocol（模型上下文协议）

# 1.2 MCP 和 Function Calling 最大的区别是什么？
# A. MCP 更快
# B. MCP 支持动态发现工具，Function Calling 需要硬编码
# C. MCP 只能本地用
# D. MCP 不支持参数
# 答案：B

# 1.3 MCP 的架构包含哪两个角色？
# 答案：Client（AI 应用）和 Server（工具提供方）

# 1.4 MCP Server 通过什么方式暴露工具？
# 答案：tools/list（列出工具）和 tools/call（调用工具）

print("=== 题目 1: MCP 概念 ===")
print("MCP = Model Context Protocol")
print("核心：Client ←→ Server，工具自动发现")
print("vs Function Calling：动态发现 vs 硬编码")


# --- 题目 2: 写最小 MCP Server（模拟）---

# TODO 2.1: 实现一个模拟 MCP Server
class MCPServer:
    """模拟 MCP Server"""

    def __init__(self, name):
        self.name = name
        self._tools = {}

    def register_tool(self, name, description, fn, parameters=None):
        """注册工具"""
        self._tools[name] = {
            "name": name,
            "description": description,
            "fn": fn,
            "inputSchema": parameters or {},
        }

    def list_tools(self):
        """tools/list — 返回所有工具"""
        return [
            {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
            for t in self._tools.values()
        ]

    def call_tool(self, name, arguments=None):
        """tools/call — 调用工具"""
        if name not in self._tools:
            return {"error": f"Tool '{name}' not found"}
        try:
            result = self._tools[name]["fn"](arguments or {})
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            return {"error": str(e)}


# TODO 2.2: 注册 3 个工具
server = MCPServer("practice-tools")

server.register_tool(
    "get_time",
    "获取当前时间",
    lambda args: datetime.now().strftime(args.get("format", "%Y-%m-%d %H:%M:%S")),
    {"type": "object", "properties": {"format": {"type": "string"}}},
)

server.register_tool(
    "random_number",
    "生成指定范围的随机数",
    lambda args: random.randint(args.get("min", 1), args.get("max", 100)),
    {"type": "object", "properties": {"min": {"type": "integer"}, "max": {"type": "integer"}}},
)

server.register_tool(
    "text_length",
    "统计文本长度",
    lambda args: len(args.get("text", "")),
    {"type": "object", "properties": {"text": {"type": "string"}}},
)

print("\n=== 题目 2: MCP Server ===")
tools = server.list_tools()
print(f"Server '{server.name}' 提供 {len(tools)} 个工具:")
for t in tools:
    print(f"  - {t['name']}: {t['description']}")


# --- 题目 3: MCP Client 连接 ---

# TODO 3.1: 实现 MCP Client
class MCPClient:
    """模拟 MCP Client"""

    def __init__(self, server):
        self.server = server
        self.tools = []

    def connect(self):
        """连接并发现工具"""
        self.tools = self.server.list_tools()
        print(f"  ✅ 已连接，发现 {len(self.tools)} 个工具")
        return self.tools

    def call(self, tool_name, arguments=None):
        """调用工具"""
        return self.server.call_tool(tool_name, arguments)

    def get_tool_names(self):
        """获取所有工具名"""
        return [t["name"] for t in self.tools]


# 测试
print("\n=== 题目 3: MCP Client ===")
mcp_client = MCPClient(server)
mcp_client.connect()

# 调用每个工具
print("\n调用测试:")
print(f"  get_time: {mcp_client.call('get_time')}")
print(f"  random_number: {mcp_client.call('random_number', {'min': 1, 'max': 10})}")
print(f"  text_length: {mcp_client.call('text_length', {'text': 'Hello MCP!'})}")
print(f"  不存在: {mcp_client.call('xxx')}")


# --- 题目 4: MCP 工具集成到 LLM ---

# TODO 4.1: 把 MCP 工具转成 LLM 能理解的文本描述
def tools_to_prompt(mcp_client):
    """
    将 MCP 工具列表转成 prompt 文本

    返回:
        "可用工具：\n- get_time: 获取当前时间\n- ..."
    """
    lines = ["可用工具："]
    for tool in mcp_client.tools:
        lines.append(f"- {tool['name']}: {tool['description']}")
    return "\n".join(lines)


# TODO 4.2: 根据 LLM 输出调用 MCP 工具
def call_tool_from_llm_output(mcp_client, tool_name, args_str):
    """
    解析 LLM 输出的工具名和参数，调用 MCP 工具

    参数:
        tool_name: LLM 选择的工具名
        args_str: LLM 给出的参数（JSON 字符串）
    """
    try:
        args = json.loads(args_str) if args_str else {}
    except json.JSONDecodeError:
        args = {"text": args_str}

    return mcp_client.call(tool_name, args)


print("\n=== 题目 4: MCP + LLM 集成 ===")
prompt_text = tools_to_prompt(mcp_client)
print(prompt_text)

# 模拟 LLM 选择了 get_time 工具
result = call_tool_from_llm_output(mcp_client, "get_time", '{"format": "%H:%M"}')
print(f"\n模拟 LLM 调用 get_time: {result}")

result = call_tool_from_llm_output(mcp_client, "random_number", '{"min": 50, "max": 100}')
print(f"模拟 LLM 调用 random_number: {result}")
