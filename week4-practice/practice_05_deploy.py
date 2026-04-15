# ===========================================
# 练习 5：部署上线（对应 Day 5）
# ===========================================
# 不看教程，自己写！
# 卡住了再回去看 05_deployment.py / 05_deployment.md
# ===========================================

import time
import json
import logging
from pathlib import Path


# --- 题目 1: 生成 requirements.txt ---

# TODO 1.1: 扫描项目目录，生成依赖列表
def generate_requirements(project_dir, output_path=None):
    """
    扫描 .py 文件的 import 语句，生成 requirements.txt
    """
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

    found = set()
    for py_file in Path(project_dir).glob("**/*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for imp_name, pip_name in KNOWN_DEPS.items():
            if f"import {imp_name}" in content or f"from {imp_name}" in content:
                found.add(pip_name)

    deps = sorted(found)
    result = "\n".join(deps) + "\n"

    if output_path:
        Path(output_path).write_text(result, encoding="utf-8")

    return deps


# 测试
print("=== 题目 1: requirements.txt ===")
project = Path(__file__).parent.parent / "week4-project"
if project.exists():
    deps = generate_requirements(project)
    print(f"  找到 {len(deps)} 个依赖:")
    for d in deps:
        print(f"    {d}")
else:
    # 用 week4-agent-and-deploy 演示
    deps = generate_requirements(Path(__file__).parent.parent / "week4-agent-and-deploy")
    print(f"  (week4-project 未创建，扫描教程目录)")
    print(f"  找到 {len(deps)} 个依赖:")
    for d in deps:
        print(f"    {d}")


# --- 题目 2: 编写 Dockerfile ---

# TODO 2.1: 生成 Dockerfile 内容
def generate_dockerfile(python_version="3.11", port=8000, start_cmd="uvicorn main:app --host 0.0.0.0 --port 8000"):
    """生成 Dockerfile 内容"""
    return f"""FROM python:{python_version}-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE {port}

CMD {json.dumps(start_cmd.split())}
"""


print("\n=== 题目 2: Dockerfile ===")
dockerfile = generate_dockerfile()
print(dockerfile)


# --- 题目 3: 环境变量模板 ---

# TODO 3.1: 从 .env 生成 .env.example
def generate_env_example(env_path, output_path=None):
    """
    把 .env 的值替换成占位符
    """
    env_file = Path(env_path)
    if not env_file.exists():
        return "# .env 文件不存在\n"

    lines = []
    for line in env_file.read_text(encoding="utf-8").strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            lines.append(line)
        elif "=" in line:
            key = line.split("=", 1)[0]
            lines.append(f"{key}=your_{key.lower()}_here")

    result = "\n".join(lines) + "\n"
    if output_path:
        Path(output_path).write_text(result, encoding="utf-8")
    return result


print("=== 题目 3: .env.example ===")
env_example = generate_env_example(Path(__file__).parent / ".env")
print(env_example)


# --- 题目 4: 日志中间件 ---

# TODO 4.1: 写一个 FastAPI 日志中间件（代码字符串演示）
middleware_code = '''
import time
import json
import logging
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
'''

print("=== 题目 4: 日志中间件 ===")
print(middleware_code)

# 演示 Python logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("practice")

logger.info("应用启动")
logger.info(json.dumps({"event": "request", "method": "POST", "path": "/api/ask", "status": 200, "latency_ms": 1234}))
logger.warning("API 延迟偏高: 3200ms")
logger.error("模型调用失败: timeout")

print("\n部署文件清单:")
print("  ✅ requirements.txt")
print("  ✅ Dockerfile")
print("  ✅ .env.example")
print("  ✅ 日志中间件")
