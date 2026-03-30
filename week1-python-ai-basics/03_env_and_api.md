# Day 3：虚拟环境 + pip + 第一次调用 AI API

## 学习内容

1. **虚拟环境 (venv)** — 隔离项目依赖，等价于 Node.js 的 node_modules
2. **pip 包管理** — 等价于 npm/yarn
3. **requirements.txt** — 等价于 package.json 的 dependencies
4. **环境变量与 .env** — 安全管理 API Key
5. **调用 AI API** — 用 httpx 和官方 SDK 两种方式调用 Claude API

## npm vs pip 速查

| 概念 | Node.js | Python |
|------|---------|--------|
| 创建项目环境 | `npm init` | `python -m venv venv` |
| 激活环境 | 自动（node_modules） | `source venv/Scripts/activate`（Windows Git Bash） |
| 安装包 | `npm install axios` | `pip install httpx` |
| 安装全部依赖 | `npm install` | `pip install -r requirements.txt` |
| 依赖文件 | `package.json` | `requirements.txt` |
| 锁定版本 | `package-lock.json` | `pip freeze > requirements.txt` |
| 全局安装 | `npm install -g` | `pip install`（不在 venv 中时） |
| 运行脚本 | `npm run dev` | `python main.py` |

## 注意事项

- **必须激活虚拟环境**：安装包前先 `activate`，否则会装到全局 Python
- **永远不要把 .env 提交到 git**：API Key 泄露会被盗用产生费用
- **requirements.txt 要及时更新**：每次装新包后 `pip freeze > requirements.txt`
- **API 调用有费用**：Claude/OpenAI API 按 token 计费，学习阶段用短 prompt 控制成本
- **流式输出是重点**：后面做 AI 应用必须掌握 stream 模式，用户体验差别巨大
