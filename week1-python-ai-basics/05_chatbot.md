# Day 5：实战项目 — 命令行 AI 聊天机器人

## 学习内容

1. **项目结构组织** — 把代码拆分成多个模块，告别单文件
2. **配置管理** — 统一管理 API 配置，方便切换模型
3. **多轮对话管理** — 维护对话历史，实现上下文记忆
4. **流式输出** — 逐字打印，提升用户体验
5. **指令系统** — 实现 `/help`、`/clear`、`/save` 等斜杠命令
6. **对话持久化** — 把聊天记录保存为 JSON 文件

## 项目结构

```
week1-python-ai-basics/
├── chatbot/
│   ├── __init__.py      # 让 Python 把这个文件夹当作模块
│   ├── config.py        # 配置管理（API Key、模型名等）
│   ├── client.py        # AI 客户端封装
│   └── commands.py      # 斜杠命令处理
├── 05_chatbot.py        # 主入口
└── ...
```

## 知识点对照

| 概念 | 前端等价物 | Python 实现 |
|------|-----------|------------|
| 模块拆分 | `import { x } from './utils'` | `from chatbot.config import Config` |
| `__init__.py` | `index.js` | 模块入口文件 |
| 配置管理 | `.env` + `config.ts` | `dataclass` + `dotenv` |
| 数据类 | TypeScript `interface` | `@dataclass` 装饰器 |
| JSON 读写 | `fs.readFileSync` / `writeFileSync` | `json.load()` / `json.dump()` |

## 注意事项

- **`__init__.py` 不能省**：没有它 Python 不会把文件夹当作可导入的包
- **dataclass 很好用**：类似 TypeScript 的 interface，定义数据结构用它就对了
- **对话历史会越来越长**：每次请求都带全部历史，token 消耗会增长，实际项目需要截断策略
- **异常处理要完善**：网络请求随时可能失败，一定要用 try/except
- **`if __name__ == "__main__"`**：Python 的入口判断，类似 Node 的模块直接运行 vs 被导入
