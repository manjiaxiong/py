# ===========================================
# Day 5: 部署上线 — 把项目部署到云端
# ===========================================
# 开发完成后最后一步：让别人也能访问你的项目
#
# 类比：
# 前端：npm run build → vercel deploy
# Python：pip freeze → Railway / Docker deploy
#
# 前端类比：
# Railway   = Vercel（Python 版），push 就部署
# Docker    = 更灵活的部署方式，打包成镜像
# Render    = 另一个 Vercel-like 平台
# ===========================================

import sys
import os
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv(Path(__file__).parent / ".env")


# ===========================================
# 1. 部署方案对比
# ===========================================
# 三种主流方案：Railway / Render / Docker
#
# JS 类比：
# Railway = Vercel for Python（push 就部署）
# Render  = Netlify for Python（免费额度）
# Docker  = 自己打包，到处能跑

print("=== Section 1: 部署方案对比 ===")
print("┌──────────┬──────────┬──────────┬──────────────┐")
print("│ 方案      │ 难度     │ 费用      │ 适合场景      │")
print("├──────────┼──────────┼──────────┼──────────────┤")
print("│ Railway  │ ⭐ 最简单 │ $5/月起   │ 快速上线demo  │")
print("│ Render   │ ⭐ 简单   │ 有免费额度 │ 个人项目      │")
print("│ Docker   │ ⭐⭐ 中等 │ 看平台    │ 生产环境      │")
print("└──────────┴──────────┴──────────┴──────────────┘")
print()


# ===========================================
# 2. 准备项目部署
# ===========================================
# 部署前需要准备的文件：
# 1. requirements.txt — 依赖列表
# 2. Procfile — 启动命令（Railway/Render 用）
# 3. runtime.txt — Python 版本
# 4. .env.example — 环境变量模板

def generate_requirements(project_dir, output_path=None):
    """
    生成 requirements.txt

    扫描 .py 文件中的 import 语句，匹配已知依赖

    JS 类比：
    package.json 的 dependencies 列表
    """
    # 常用依赖映射（import名 → pip包名）
    KNOWN_DEPS = {
        "fastapi": "fastapi>=0.100.0",
        "uvicorn": "uvicorn>=0.23.0",
        "pydantic": "pydantic>=2.0.0",
        "anthropic": "anthropic>=0.25.0",
        "dotenv": "python-dotenv>=1.0.0",
        "chromadb": "chromadb>=0.4.0",
        "sse_starlette": "sse-starlette>=1.6.0",
        "langgraph": "langgraph>=0.2.0",
        "langchain": "langchain>=0.2.0",
        "langchain_core": "langchain-core>=0.2.0",
        "mcp": "mcp>=1.0.0",
        "httpx": "httpx>=0.25.0",
    }

    found_deps = set()
    project_path = Path(project_dir)

    for py_file in project_path.glob("**/*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for imp_name, pip_name in KNOWN_DEPS.items():
            if f"import {imp_name}" in content or f"from {imp_name}" in content:
                found_deps.add(pip_name)

    # 排序
    deps = sorted(found_deps)

    output = output_path or project_path / "requirements.txt"
    Path(output).write_text("\n".join(deps) + "\n", encoding="utf-8")

    print(f"  📦 生成 requirements.txt ({len(deps)} 个依赖)")
    for d in deps:
        print(f"     {d}")

    return deps


def generate_procfile(start_command="uvicorn main:app --host 0.0.0.0 --port $PORT", output_path=None):
    """
    生成 Procfile（Railway / Render / Heroku 用）

    JS 类比：package.json 的 "start" script
    """
    content = f"web: {start_command}\n"
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    print(f"  📄 Procfile: {start_command}")
    return content


def generate_runtime(python_version="3.11", output_path=None):
    """生成 runtime.txt"""
    content = f"python-{python_version}\n"
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    print(f"  🐍 runtime.txt: python-{python_version}")
    return content


print("=== Section 2: 准备部署文件 ===")
# 给 week4-project 生成部署文件
project_dir = Path(__file__).parent.parent / "week4-project"
if project_dir.exists():
    generate_requirements(project_dir)
else:
    print("  (week4-project 目录还未创建，跳过)")
print()


# ===========================================
# 3. Docker 部署
# ===========================================
# Docker = 把整个运行环境打包成镜像
# 好处：在你电脑能跑，在服务器也能跑（一致性）
#
# JS 类比：
# Dockerfile = 一个自动化的 npm install + npm start
# docker-compose = 多个服务的编排（前端 + 后端 + 数据库）

DOCKERFILE_TEMPLATE = """# Python FastAPI Dockerfile
# 构建方式: docker build -t my-ai-app .
# 运行方式: docker run -p 8000:8000 --env-file .env my-ai-app

# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

DOCKER_COMPOSE_TEMPLATE = """# docker-compose.yml
# 启动方式: docker-compose up -d
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./docs:/app/docs    # 挂载文档目录
    restart: unless-stopped
"""

print("=== Section 3: Docker 部署 ===")
print("Dockerfile 模板:")
print(DOCKERFILE_TEMPLATE[:200] + "...\n")

# 保存 Docker 文件到教程目录（仅作参考）
# (Path(__file__).parent / "Dockerfile.example").write_text(DOCKERFILE_TEMPLATE)
# (Path(__file__).parent / "docker-compose.example.yml").write_text(DOCKER_COMPOSE_TEMPLATE)


# ===========================================
# 4. 环境变量与安全
# ===========================================
# .env 文件绝对不能提交到 git！
# 部署平台上用环境变量配置（不是文件）
#
# JS 类比：
# .env.local → 本地开发用
# Vercel Environment Variables → 线上用
# 同理：
# .env → 本地开发用
# Railway/Render 环境变量设置 → 线上用

def generate_env_example(env_path, output_path=None):
    """
    从 .env 生成 .env.example（隐藏值）

    .env:
        MINIMAX_API_KEY=sk-xxx123
    .env.example:
        MINIMAX_API_KEY=your_api_key_here
    """
    env_file = Path(env_path)
    if not env_file.exists():
        print("  ⚠️ .env 文件不存在")
        return ""

    lines = []
    for line in env_file.read_text(encoding="utf-8").strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            lines.append(line)
            continue
        if "=" in line:
            key = line.split("=", 1)[0]
            lines.append(f"{key}=your_{key.lower()}_here")

    result = "\n".join(lines) + "\n"
    if output_path:
        Path(output_path).write_text(result, encoding="utf-8")
        print(f"  📄 .env.example 已生成")

    return result


print("=== Section 4: 环境变量安全 ===")
print("安全规则:")
print("  1. .env 加入 .gitignore（已做）")
print("  2. 提供 .env.example（隐藏值）")
print("  3. 线上用平台环境变量，不用文件")
print("  4. API Key 定期轮换")
print()

# 生成 .env.example
env_example = generate_env_example(
    Path(__file__).parent / ".env",
    Path(__file__).parent / ".env.example",
)
if env_example:
    print(f"  .env.example 内容:\n{env_example}")


# ===========================================
# 5. 错误日志与监控
# ===========================================
# 线上项目必须有日志 — 出了问题要能查
#
# JS 类比：
# console.log → print（开发用）
# Winston/Pino → logging（生产用）
# Sentry → 错误追踪
# Web Vitals → 性能监控

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# FastAPI 日志中间件
MIDDLEWARE_CODE = '''
import time
import json
import logging
from fastapi import Request

logger = logging.getLogger("api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件

    记录每次请求的：方法、路径、状态码、耗时

    JS 类比：
    app.use((req, res, next) => {
        const start = Date.now();
        res.on('finish', () => {
            console.log(`${req.method} ${req.path} ${res.statusCode} ${Date.now()-start}ms`);
        });
        next();
    });
    """
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
'''

print("=== Section 5: 错误日志与监控 ===")
print("FastAPI 日志中间件示例:")
print(MIDDLEWARE_CODE[:300] + "...\n")

# 演示 logging
logger.info("应用启动")
logger.info(json.dumps({"event": "eval_complete", "pass_rate": 0.8, "latency_ms": 1500}))
logger.warning("API 延迟偏高: 3.2s")

print("\n部署清单:")
print("  ✅ requirements.txt — 依赖列表")
print("  ✅ Procfile — 启动命令")
print("  ✅ Dockerfile — Docker 部署")
print("  ✅ .env.example — 环境变量模板")
print("  ✅ 日志中间件 — 请求追踪")
print("  ✅ .gitignore — 排除敏感文件")
