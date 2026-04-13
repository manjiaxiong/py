# API 设计最佳实践

## RESTful API 规范

### URL 设计

1. 用名词不用动词：`/users` 而不是 `/getUsers`
2. 用复数：`/users` 而不是 `/user`
3. 嵌套表示关系：`/users/123/orders`
4. 用查询参数做筛选：`/users?role=admin&page=1`

### HTTP 方法

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 获取资源 | GET /users |
| POST | 创建资源 | POST /users |
| PUT | 全量更新 | PUT /users/123 |
| PATCH | 部分更新 | PATCH /users/123 |
| DELETE | 删除资源 | DELETE /users/123 |

### 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | GET/PUT/PATCH 成功 |
| 201 | 已创建 | POST 成功 |
| 204 | 无内容 | DELETE 成功 |
| 400 | 请求错误 | 参数校验失败 |
| 401 | 未认证 | 没有登录/token 过期 |
| 403 | 无权限 | 登录了但没有权限 |
| 404 | 未找到 | 资源不存在 |
| 422 | 实体不可处理 | 数据格式正确但语义错误 |
| 500 | 服务器错误 | 后端代码出 bug |

## 请求和响应格式

### 请求体

```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "role": "admin"
}
```

### 成功响应

```json
{
  "code": 0,
  "data": {
    "id": 123,
    "name": "Alice"
  },
  "message": "success"
}
```

### 错误响应

```json
{
  "code": 400,
  "error": "validation_error",
  "message": "email 格式不正确",
  "details": [
    {"field": "email", "message": "必须是有效的邮箱地址"}
  ]
}
```

## 分页

```
GET /users?page=1&page_size=20
```

响应：
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

## 认证方式

### Bearer Token

最常用的方式，前端在请求头带上 token：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

### API Key

适合服务端对服务端的调用：

```
X-API-Key: sk-xxxxx
```

## 版本控制

推荐在 URL 中加版本号：

```
/api/v1/users
/api/v2/users
```

## 限流（Rate Limiting）

防止接口被滥用，常用策略：

1. 固定窗口：每分钟最多 60 次请求
2. 滑动窗口：更平滑的限流
3. Token Bucket：允许短时突发

响应头中返回限流信息：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1620000000
```

## CORS（跨域资源共享）

前后端分离项目必须配置 CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 流式响应（SSE）

AI 应用常用 Server-Sent Events 实现流式输出：

```python
from sse_starlette.sse import EventSourceResponse

@app.get("/stream")
async def stream():
    async def generate():
        for chunk in ai_response:
            yield {"data": chunk}
    return EventSourceResponse(generate())
```

前端接收：

```javascript
const source = new EventSource("/stream");
source.onmessage = (event) => {
    console.log(event.data);
};
```

## AI API 设计要点

1. 请求体要有 `stream` 参数，让前端选择是否流式
2. 返回中要包含 `tokens_used`，方便成本统计
3. 支持 `conversation_id` 实现多轮对话
4. 错误要区分：模型错误 vs 业务错误
5. 设置合理的超时时间（AI 请求通常较慢）
