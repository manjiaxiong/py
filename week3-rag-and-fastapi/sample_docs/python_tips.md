# Python 开发实用技巧

## 虚拟环境管理

每个项目都应该有独立的虚拟环境，避免依赖冲突。

```bash
# 创建虚拟环境
python -m venv venv

# 激活（Windows Git Bash）
source venv/Scripts/activate

# 激活（Mac/Linux）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 导出依赖
pip freeze > requirements.txt
```

## 常用数据结构

### 列表推导式

列表推导式是 Python 最强大的特性之一，一行代码搞定 filter + map。

```python
# 基础
squares = [x**2 for x in range(10)]

# 带条件
evens = [x for x in range(20) if x % 2 == 0]

# 嵌套
flat = [x for row in matrix for x in row]
```

### 字典操作

```python
# 安全取值
value = d.get("key", "默认值")

# 字典推导式
scores = {name: score for name, score in data if score > 60}

# 合并字典
merged = {**dict1, **dict2}
```

## 异常处理最佳实践

1. 捕获具体异常，不要用 bare except
2. 用 try/except/else/finally 完整处理
3. 自定义异常类提高可读性

```python
try:
    result = api_call()
except ConnectionError as e:
    print(f"网络错误: {e}")
except json.JSONDecodeError:
    print("JSON 解析失败")
else:
    print(f"成功: {result}")
finally:
    cleanup()
```

## 异步编程

Python 的 async/await 和 JavaScript 几乎一样，但需要 asyncio 驱动。

```python
import asyncio

async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# 并行请求（= Promise.all）
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3),
)
```

## 文件操作

```python
from pathlib import Path

# 读文件
text = Path("data.txt").read_text(encoding="utf-8")

# 写文件
Path("output.txt").write_text(result, encoding="utf-8")

# 遍历目录
for f in Path("docs").glob("*.md"):
    print(f.name)
```

## 类型提示

Python 类型提示不强制，但能提升代码可读性和 IDE 补全。

```python
from typing import List, Dict, Optional

def process(items: List[str], config: Optional[Dict] = None) -> str:
    ...
```

配合 Pydantic 可以实现运行时类型校验：

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: Optional[str] = None
```

## 装饰器

装饰器本质是高阶函数，接收函数返回函数。

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

## 环境变量管理

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
```

永远不要把 API Key 硬编码在代码里，用 .env 文件 + .gitignore 管理。
