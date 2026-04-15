# Day 4: 评估与优化 — 项目级质量保障

## 学习目标

- 理解为什么 AI 项目必须有评估
- 能设计评估集并跑评估
- 学会分析失败原因并分类
- 掌握多轮调优对比方法
- 能生成调优报告

## 为什么需要评估

| 场景 | 不做评估 | 做了评估 |
|------|---------|---------|
| 改了 prompt | 不知道是否破坏了已有功能 | 跑回归测试，立刻发现问题 |
| 换了模型 | 凭感觉判断好坏 | 有数据对比 |
| 加了工具 | 不知道是否更好 | 看通过率和延迟变化 |
| 上线前 | 心里没底 | 数据说话 |

### JS 类比

```javascript
// 前端有测试 → AI 也要有评估
// Jest/Vitest    → eval_runner.py
// test cases     → eval_cases.json
// expect(x).toBe → keywords matching
// CI pipeline    → 改 prompt 后自动跑评估
```

## 评估集设计

### 结构

```json
[
  {
    "id": "case_001",
    "input": "用户输入",
    "expected_keywords": ["期望关键词1", "关键词2"],
    "tags": ["分类标签"]
  }
]
```

### 设计原则

| 原则 | 说明 |
|------|------|
| 覆盖核心场景 | 最常见的用户问题必须有 |
| 包含边界情况 | 空输入、超长输入、无关问题 |
| 有正有负 | 既要能答的，也要该拒答的 |
| 可重复 | 同一用例多次运行结果应稳定 |
| 持续增长 | 每次发现 bug 就加一条 |

## 失败分析

### 失败原因分类

```
                    ┌─────────────┐
                    │   评估失败   │
                    └──────┬──────┘
           ┌───────┬───────┼───────┬───────┐
           ↓       ↓       ↓       ↓       ↓
        Prompt  工具描述  检索质量  模型能力  上下文
        不清晰  有歧义   不相关   不足     太长
```

| 原因 | 表现 | 解决方案 |
|------|------|---------|
| Prompt 不清晰 | 回答跑题或格式错误 | 优化 system prompt |
| 工具描述有歧义 | Agent 选错工具 | 改工具 description |
| 检索结果不相关 | RAG 答非所问 | 调 chunk_size / top_k |
| 模型能力不足 | 简单问题也答错 | 换更强模型 |
| 上下文太长 | 关键信息被截断 | 减少 context 长度 |

### JS 类比

```javascript
// Sentry 错误分类
// TypeError → 代码 bug
// NetworkError → 网络问题
// ChunkLoadError → 部署问题

// AI 失败分类
// 完全不匹配 → prompt 问题
// 部分匹配 → 需要优化
// 简单题出错 → 模型问题
```

## 多轮调优

### 流程

```
Round 1: baseline（无 system prompt） → 记录通过率
     ↓
Round 2: 加 system prompt（简洁版） → 对比通过率
     ↓
Round 3: 加 system prompt（详细版） → 对比通过率
     ↓
选最优配置
```

### 对比代码

```python
PROMPTS = {
    "baseline": "",
    "concise": "简洁回答，50字以内",
    "detailed": "详细回答，包含术语和示例",
}

for name, prompt in PROMPTS.items():
    result = run_eval(eval_cases, client, model, system_prompt=prompt)
    print(f"{name}: {result['pass_rate']:.0%}")
```

## 延迟与成本追踪

### 装饰器

```python
import time, functools

def track_latency(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        latency = time.time() - start
        metrics.append({"fn": fn.__name__, "ms": round(latency*1000, 1)})
        return result
    return wrapper

@track_latency
def ask_tracked(client, model, prompt, **kwargs):
    return ask(client, model, prompt, **kwargs)
```

```javascript
// JS 类比
const withTiming = (fn) => async (...args) => {
  const t0 = performance.now();
  const result = await fn(...args);
  console.log(`${fn.name}: ${performance.now() - t0}ms`);
  return result;
};
```

### 优化策略

| 策略 | 效果 | JS 类比 |
|------|------|---------|
| 减少 max_tokens | 降低延迟和成本 | 减少 bundle size |
| 缓存重复查询 | 避免重复调用 | HTTP 缓存 / memo |
| 并行调用 | 多个独立查询同时跑 | Promise.all |
| 用更快模型 | 延迟更低 | CDN 加速 |

## 调优报告

```markdown
# AI 系统评估与调优报告

- 评估时间: 2026-04-15
- 评估用例: 5 条
- 基线通过率: 80%
- 平均延迟: 1500ms

## 配置对比

| 配置 | 通过率 | 平均延迟 |
|---|---|---|
| baseline | 80% | 1500ms |
| concise | 60% | 800ms |
| detailed | 100% | 2200ms |

## 优化建议

- 选择 detailed 配置（通过率最高）
- 延迟可接受（2.2s）
```

## 关键要点

1. **评估集 = AI 的测试用例** — 改 prompt 前后都要跑
2. **失败要分类** — 知道原因才能对症下药
3. **多轮对比** — 同一评估集，不同配置，用数据说话
4. **追踪延迟和成本** — 不只看效果，还要看性价比
5. **持续迭代** — 评估集跟着产品需求一起增长

## 推荐资源

- [Anthropic 评估指南](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [OpenAI Evals](https://github.com/openai/evals)
- [RAGAS (RAG Assessment)](https://github.com/explodinggradients/ragas)
