# Day 5: 部署上线 — 把项目部署到云端

## 学习目标

- 了解 Python 项目的部署方案
- 能生成部署所需的配置文件
- 理解 Docker 部署流程
- 掌握环境变量安全管理
- 能为 FastAPI 项目添加日志中间件

## 部署方案对比

| 方案 | 难度 | 费用 | 适合场景 | JS 类比 |
|------|------|------|---------|---------|
| Railway | 最简单 | $5/月起 | 快速上线 demo | Vercel |
| Render | 简单 | 有免费额度 | 个人项目 | Netlify |
| Docker | 中等 | 看平台 | 生产环境 | 自建 CI/CD |

### Railway 部署流程

```
1. 推代码到 GitHub
2. Railway 连接 GitHub 仓库
3. 自动检测 Python 项目
4. 配置环境变量
5. 自动部署 ✅
```

```javascript
// JS 类比：Vercel 部署
// 1. git push
// 2. Vercel 自动构建
// 3. 配置 env vars
// 4. 自动部署
```

## 部署文件清单

### requirements.txt

```
anthropic>=0.25.0
chromadb>=0.4.0
fastapi>=0.100.0
langgraph>=0.2.0
pydantic>=2.0.0
python-dotenv>=1.0.0
sse-starlette>=1.6.0
uvicorn>=0.23.0
```

```javascript
// JS 类比：package.json 的 dependencies
{
  "dependencies": {
    "express": "^4.18.0",
    "openai": "^4.0.0"
  }
}
```

### Procfile

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

```javascript
// JS 类比：package.json 的 start script
{ "scripts": { "start": "node server.js" } }
```

### runtime.txt

```
python-3.11
```

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# 先装依赖（利用缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制代码
COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

### 常用命令

```bash
# 构建镜像
docker build -t my-ai-app .

# 运行容器
docker run -p 8000:8000 --env-file .env my-ai-app

# docker-compose 启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### JS 类比

```javascript
// Docker 就像一个自动化的安装+启动脚本
// Dockerfile = npm install + npm start 的自动化版本
// docker-compose = PM2 ecosystem.config.js（多服务编排）
```

## 环境变量安全

### 规则

| 规则 | 说明 |
|------|------|
| .env 不提交 | 加入 .gitignore |
| 提供 .env.example | 隐藏值，写占位符 |
| 线上用平台设置 | Railway/Render 的 env vars 面板 |
| Key 定期轮换 | 泄露了立刻换 |

### .env vs .env.example

```
# .env（本地开发用，不提交）
MINIMAX_API_KEY=sk-KHTsL3FFqyy5ZvcOAQz8rA
MINIMAX_API_BASE=http://models.cm253.com:4001

# .env.example（提交到 git，给其他人参考）
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_API_BASE=your_minimax_api_base_here
```

## 错误日志与监控

### FastAPI 日志中间件

```python
import time, json, logging
from fastapi import Request

logger = logging.getLogger("api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start

    logger.info(json.dumps({
        "method": request.method,
        "path": str(request.url.path),
        "status": response.status_code,
        "latency_ms": round(latency * 1000, 1),
    }))
    return response
```

```javascript
// JS 类比：Express 日志中间件
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    console.log(JSON.stringify({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      latency_ms: Date.now() - start,
    }));
  });
  next();
});
```

### 日志级别

| 级别 | 用途 | JS 类比 |
|------|------|---------|
| DEBUG | 开发调试 | console.debug |
| INFO | 正常运行信息 | console.log |
| WARNING | 潜在问题 | console.warn |
| ERROR | 错误 | console.error |

## 部署清单

- [ ] requirements.txt — 依赖列表
- [ ] Procfile — 启动命令
- [ ] Dockerfile + docker-compose.yml
- [ ] .env.example — 环境变量模板
- [ ] .gitignore — 排除 .env、__pycache__
- [ ] 日志中间件 — 请求追踪
- [ ] 健康检查接口 — GET /health
- [ ] README.md — 部署说明

## 关键要点

1. **Railway 最适合快速部署** — push 就上线，类似 Vercel
2. **Docker 最适合生产** — 打包环境，一致性强
3. **.env 绝不提交 git** — 用 .env.example 代替
4. **日志是线上必需品** — 出问题时唯一的线索
5. **先跑通本地，再部署** — 别在线上 debug

## 推荐资源

- [Railway 部署 Python](https://docs.railway.app/guides/python)
- [Render 部署 FastAPI](https://render.com/docs/deploy-fastapi)
- [Docker 官方 Python 指南](https://docs.docker.com/language/python/)
- [FastAPI 部署文档](https://fastapi.tiangolo.com/deployment/)
