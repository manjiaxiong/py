# ===========================================
# AI 笔记生成模块
# ===========================================
# 负责调用 AI API 为代码文件生成学习笔记
# 用到: AsyncAnthropic（异步客户端）、asyncio.gather（并行调用）、装饰器
# ===========================================

import json
import time
import asyncio
import inspect
import functools
from pathlib import Path
from anthropic import AsyncAnthropic


# ===========================================
# 装饰器：计时器
# ===========================================
# 用来测量函数执行时间，方便知道 AI 调用花了多久
# JS 类比: console.time('label') + console.timeEnd('label')

def timer(func):
    """
    计时装饰器 — 打印函数执行时间

    这里用 @functools.wraps 保留原函数的名字和文档
    不加的话，被装饰后 func.__name__ 会变成 "wrapper"

    ⚠️ 这个装饰器支持异步函数:
    - 用 asyncio.iscoroutinefunction() 判断是不是 async 函数
    - 如果是 async，用 await 调用；否则直接调用
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} 执行时间: {elapsed:.2f}秒")
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} 执行时间: {elapsed:.2f}秒")
        return result

    # 根据原函数类型返回对应的 wrapper
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# ===========================================
# AI 笔记生成器
# ===========================================

class NoteGenerator:
    """
    AI 笔记生成器 — 用 AI 为代码文件生成学习笔记

    核心流程:
    1. 读取 .py 文件内容
    2. 发送给 AI，要求返回 JSON 格式的学习笔记
    3. 解析 AI 返回的 JSON
    4. 汇总所有笔记，生成 Markdown 报告

    JS 类比:
    class NoteGenerator {
      constructor(config) {
        this.client = new Anthropic({ apiKey: config.apiKey })
      }
      async generateNote(fileContent) { ... }
      async generateAll(files) {
        return Promise.all(files.map(f => this.generateNote(f)))  // 并行调用
      }
    }
    """

    def __init__(self, config, scanner):
        """
        参数:
            config: Config 实例（包含 API key、model 等配置）
            scanner: Scanner 实例（用来读取文件内容）

        AsyncAnthropic = 异步版的 Anthropic 客户端
        普通的 Anthropic 是同步的（一个一个调用）
        异步的可以用 asyncio.gather() 并行调用多个 API
        JS 类比: 同步 = 用 for 循环依次 await
                异步 = 用 Promise.all() 并行
        """
        self.config = config
        self.scanner = scanner

        # 创建异步客户端
        # JS 类比: const client = new Anthropic({ apiKey, baseURL })
        self.client = AsyncAnthropic(
            api_key=config.api_key,
            base_url=config.api_base,
        )

    async def generate_note(self, file_info):
        """
        为单个文件生成学习笔记

        参数:
            file_info: scanner.scan() 返回的单个文件信息
                       {"path": "01_basics.py", "full_path": "...", ...}

        返回:
            {
                "file": "01_basics.py",
                "summary": "一句话总结",
                "key_concepts": ["知识点1", "知识点2"],
                "difficulty": "beginner",
                "js_comparison": "和 JS 的 xxx 类似"
            }

        async 函数 = JS 的 async function
        await = 等待异步操作完成（和 JS 一样）
        """
        file_path = file_info["path"]
        print(f"🔍 正在分析: {file_path}")

        try:
            # 读取文件内容
            content = self.scanner.read_file(file_info["full_path"])

            # 如果文件太大，截取前 200 行（省 token 费用）
            lines = content.split("\n")
            if len(lines) > 200:
                content = "\n".join(lines[:200])
                content += f"\n\n... (共 {len(lines)} 行，已截取前 200 行)"

            # 构造 prompt — 要求 AI 返回 JSON 格式
            # 这就是"结构化输出"：通过 prompt 约束 AI 的返回格式
            prompt = f"""分析以下 Python 代码文件，生成学习笔记。

文件名: {file_path}
代码行数: {file_info['lines']}

```python
{content}
```

请严格按以下 JSON 格式返回（不要加 markdown 代码块标记，直接返回 JSON）：
{{
  "file": "{file_path}",
  "summary": "用一句话总结这个文件的内容和用途",
  "key_concepts": ["列出3-5个核心知识点"],
  "difficulty": "beginner 或 intermediate 或 advanced",
  "js_comparison": "这个文件的内容和前端 JS 的什么概念/场景类似"
}}"""

            # 调用 AI API
            # await = 等待 API 响应（异步，不阻塞其他任务）
            response = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # 提取回复文本
            text = response.content[0].text.strip()

            # 尝试解析 JSON
            # AI 有时会在 JSON 外面包一层 ```json ... ```，需要清理
            if text.startswith("```"):
                # 去掉 markdown 代码块标记
                text = text.split("\n", 1)[1]        # 去掉第一行 ```json
                text = text.rsplit("```", 1)[0]      # 去掉最后的 ```
                text = text.strip()

            note = json.loads(text)
            print(f"✅ 完成: {file_path}")
            return note

        except json.JSONDecodeError:
            # AI 返回的不是合法 JSON（偶尔会发生）
            print(f"⚠️ {file_path}: AI 返回的不是合法 JSON，使用默认格式")
            return {
                "file": file_path,
                "summary": text if 'text' in dir() else "解析失败",
                "key_concepts": ["解析失败"],
                "difficulty": "unknown",
                "js_comparison": "解析失败",
            }
        except Exception as e:
            # 网络错误、API 限流等
            print(f"❌ {file_path}: API 调用失败 — {e}")
            return {
                "file": file_path,
                "summary": f"生成失败: {e}",
                "key_concepts": [],
                "difficulty": "unknown",
                "js_comparison": "",
            }

    @timer
    async def generate_all(self, files):
        """
        并行为所有文件生成笔记

        asyncio.gather() = JS 的 Promise.all()
        把多个异步任务打包，同时执行，等全部完成后返回结果列表

        对比串行:
            for f in files:
                note = await self.generate_note(f)   # 一个一个等，慢！

        并行:
            tasks = [self.generate_note(f) for f in files]
            notes = await asyncio.gather(*tasks)      # 同时发出，快！

        JS 类比:
            // 串行
            for (const f of files) { await generateNote(f) }
            // 并行
            await Promise.all(files.map(f => generateNote(f)))
        """
        # 列表推导式创建所有任务
        tasks = [self.generate_note(f) for f in files]

        # asyncio.gather(*tasks) 并行执行所有任务
        # * 是解包运算符，把列表展开成参数
        # gather([t1, t2, t3]) ❌
        # gather(t1, t2, t3)   ✅  → 所以需要 *tasks
        # JS 类比: Promise.all(tasks)（JS 直接传数组就行）
        notes = await asyncio.gather(*tasks)

        # gather 返回的顺序和传入的顺序一致（和 Promise.all 一样）
        return list(notes)

    @timer
    def generate_report(self, notes):
        """
        把所有笔记汇总成 Markdown 报告

        Markdown 语法:
        # 一级标题
        ## 二级标题
        - 列表项
        **加粗**

        JS 类比: 就是拼接字符串，模板字符串
        `# ${title}\n## ${subtitle}`
        """
        # 用列表收集所有行，最后 join（比字符串拼接高效）
        # JS 类比: const lines = []; lines.push(...); lines.join('\n')
        lines = []

        lines.append("# 📚 代码学习笔记报告\n")
        lines.append(f"> 自动生成于 AI 分析\n")
        lines.append(f"共分析 **{len(notes)}** 个文件\n")
        lines.append("---\n")

        # 按难度分组统计
        difficulty_map = {"beginner": "🟢 入门", "intermediate": "🟡 中级", "advanced": "🔴 高级", "unknown": "⚪ 未知"}

        for i, note in enumerate(notes, 1):
            difficulty = difficulty_map.get(note.get("difficulty", "unknown"), "⚪ 未知")

            lines.append(f"## {i}. {note.get('file', '未知文件')}\n")
            lines.append(f"**难度**: {difficulty}\n")
            lines.append(f"**概要**: {note.get('summary', '无')}\n")

            # 知识点列表
            concepts = note.get("key_concepts", [])
            if concepts:
                lines.append("**核心知识点**:\n")
                for concept in concepts:
                    lines.append(f"- {concept}")
                lines.append("")  # 空行

            # JS 对比
            js_comp = note.get("js_comparison", "")
            if js_comp:
                lines.append(f"**JS 对比**: {js_comp}\n")

            lines.append("---\n")

        return "\n".join(lines)

    def save_report(self, report_md, notes):
        """
        保存报告到文件

        同时保存:
        1. Markdown 报告（给人看的）
        2. JSON 原始数据（给程序用的，方便后续处理）
        """
        output_dir = self.config.output_dir

        # 保存 Markdown
        md_path = output_dir / "notes_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"📄 Markdown 报告: {md_path}")

        # 保存 JSON 原始数据
        json_path = output_dir / "notes_data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        print(f"📋 JSON 数据: {json_path}")

        return md_path
