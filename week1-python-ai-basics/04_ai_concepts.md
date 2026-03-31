# Day 4：大模型核心概念 — Token、Temperature、Prompt 设计

## 学习内容

1. **Token 是什么** — 大模型计费和处理的基本单位
2. **关键参数** — temperature、top_p、max_tokens 对输出的影响
3. **Prompt 设计基础** — System Prompt、Few-shot、指令清晰度
4. **模型的"幻觉"** — 为什么 AI 会胡说八道，怎么缓解
5. **动手实验** — 通过调参直观感受参数对输出的影响

## 核心概念速查

| 概念 | 解释 | 类比 |
|------|------|------|
| Token | 模型处理文本的最小单位，中文约 1-2 字 = 1 token | 像像素之于图片 |
| Temperature | 控制输出随机性，0 = 确定，1 = 随机 | 像 CSS 的 opacity，控制"创意度" |
| top_p | 控制候选词范围，0.1 = 只选最可能的词 | 像搜索结果只看前 N 个 |
| max_tokens | 限制输出长度 | 像 `maxLength` 属性 |
| System Prompt | 设定 AI 的角色和行为规则 | 像给组件传 `config` props |
| Few-shot | 在 prompt 中给几个示例 | 像给函数写单元测试当文档 |
| 幻觉 | 模型编造不存在的信息 | 像 JS 的 `undefined` 不报错却返回垃圾值 |
| stop_reason | 模型为什么停止输出 | `end_turn`=正常结束，`max_tokens`=被截断 |

## 注意事项

- **Temperature 不是越高越好**：代码生成用 0~0.3，创意写作用 0.7~1.0
- **max_tokens 要合理设置**：太小会截断回复，太大浪费费用
- **Prompt 越清晰越好**：模糊指令 → 模糊回答，具体指令 → 具体回答
- **Few-shot 非常有效**：给 2-3 个示例比长篇描述更管用
- **不要信任模型的"事实"**：涉及数字、日期、链接时务必验证
