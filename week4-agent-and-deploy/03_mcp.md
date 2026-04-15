# Day 3: MCP — Model Context Protocol

## 学习目标

- 理解 MCP 的定位和价值
- 搞清楚 MCP 和 Function Calling 的区别
- 能跑通一个 MCP Server（模拟或真实）
- 了解 MCP 工具如何集成到 Agent

## MCP 是什么

MCP（Model Context Protocol）是 Anthropic 提出的开放协议，目标是让 AI 应用能**即插即用**地接入外部工具。

### 核心思想

```
以前：每个 AI App 单独适配每个工具
  App A ←→ 搜索 API（自己写适配代码）
  App A ←→ 日历 API（又写一遍）
  App B ←→ 搜索 API（再写一遍…）

现在：工具实现 MCP Server，所有 App 通过 MCP 协议统一调用
  App A ←→ MCP ←→ 搜索 Server
  App B ←→ MCP ←→ 搜索 Server  (复用！)
  App A ←→ MCP ←→ 日历 Server
```

### JS 类比

| 类比 | 说明 |
|------|------|
| USB 接口 | 不管什么设备，插上 USB 就能用 |
| npm 包 | `npm install` 后自动可用，不用手动适配 |
| 浏览器 Extension API | 写一次扩展，所有页面都能用 |

## MCP 架构

```
┌──────────────┐                  ┌──────────────┐
│   AI 应用     │   MCP 协议       │  MCP Server  │
│  (Client)     │ ←─────────────→ │  (工具提供方)  │
│              │                  │              │
│  - 连接 Server│   消息格式：      │  - 注册工具   │
│  - 发现工具   │   JSON-RPC      │  - 处理调用   │
│  - 调用工具   │                  │  - 返回结果   │
└──────────────┘                  └──────────────┘
```

### 通信方式

| 方式 | 说明 | 适合场景 |
|------|------|---------|
| stdio | 标准输入输出 | 本地工具 |
| HTTP/SSE | 网络通信 | 远程服务 |

## MCP vs Function Calling

| 维度 | Function Calling | MCP |
|------|-----------------|-----|
| 工具定义 | 硬编码在代码/prompt 里 | Server 动态提供 |
| 修改工具 | 改代码 + 重新部署 | 只改 Server，Client 不用动 |
| 工具来源 | 本地定义 | 远程 Server 提供 |
| 发现机制 | 无（写死的） | 自动发现（tools/list） |
| 复用性 | 低（每个 App 各写一份） | 高（Server 共享给所有 App） |
| 生态 | 无标准 | 开放协议，社区共建 |

### 一句话总结

> Function Calling = 手动 import 函数
> MCP = npm install + 自动发现

## MCP 协议流程

```python
# 1. 连接
client = MCPClient(server_url)

# 2. 发现工具（tools/list）
tools = client.list_tools()
# → [{"name": "get_time", "description": "获取时间", "inputSchema": {...}}]

# 3. 调用工具（tools/call）
result = client.call_tool("get_time", {"format": "%Y-%m-%d"})
# → {"content": [{"type": "text", "text": "2026-04-15"}]}
```

```javascript
// JS 类比
const mcp = new MCPClient('http://localhost:3000');
const tools = await mcp.listTools();      // 发现
const result = await mcp.callTool('get_time', {}); // 调用
```

## 写 MCP Server

### 用 mcp SDK（真实实现）

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-tools")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_time",
            description="获取当前时间",
            inputSchema={"type": "object", "properties": {"format": {"type": "string"}}},
        ),
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "get_time":
        return [TextContent(type="text", text=datetime.now().isoformat())]
```

### JS 类比

```javascript
// MCP Server ≈ Express 服务器，但暴露的是工具而不是路由
const app = express();
app.get('/api/tools', (req, res) => res.json(toolList));
app.post('/api/tools/:name', (req, res) => {
  const result = tools[req.params.name](req.body);
  res.json(result);
});
```

## MCP 集成到 Agent

```python
# 1. Client 连接 Server → 获取工具列表
mcp_client.connect()
tools = mcp_client.available_tools

# 2. 转成 Agent 工具格式
agent_tools = {}
for tool in tools:
    agent_tools[tool["name"]] = {
        "description": tool["description"],
        "fn": lambda args, name=tool["name"]: mcp_client.call(name, args),
    }

# 3. 传给 Agent
agent = SimpleAgent(client, model, tools=agent_tools)
agent.run("帮我查一下现在几点")
```

## JS 类比总览

| MCP 概念 | JS 类比 |
|----------|---------|
| MCP 协议 | REST API 标准 / GraphQL 协议 |
| MCP Server | Express 服务器（提供工具） |
| MCP Client | fetch / axios（消费工具） |
| tools/list | GET /api/tools（发现） |
| tools/call | POST /api/tools/:name（调用） |
| Tool 定义 | OpenAPI Schema |
| stdio 通信 | 进程间通信（IPC） |
| HTTP/SSE 通信 | REST API 调用 |

## 关键要点

1. **MCP = AI 工具的 USB 接口** — 统一协议，即插即用
2. **Server 提供工具，Client 消费工具** — 职责分离
3. **自动发现** — Client 连接后自动知道有哪些工具可用
4. **与 Function Calling 互补** — 简单场景用 FC，复杂生态用 MCP
5. **了解即可** — MCP 还在早期阶段，跑通一个实验理解概念就够

## 推荐资源

- [MCP 官方网站](https://modelcontextprotocol.io/)
- [MCP 规范文档](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
