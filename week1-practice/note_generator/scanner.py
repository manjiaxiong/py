# ===========================================
# 文件扫描模块
# ===========================================
# 负责扫描目录下的 .py 文件，读取文件内容
# JS 类比: 类似于用 glob 或 fs.readdirSync 递归扫描文件
# ===========================================

from pathlib import Path


class Scanner:
    """
    文件扫描器 — 扫描目录下所有 .py 文件并读取内容

    JS 类比:
    class Scanner {
      constructor(directory) {
        this.directory = directory
      }
      scan() {
        return glob.sync('**/*.py', { cwd: this.directory })
      }
    }
    """

    def __init__(self, directory):
        """
        参数:
            directory: 要扫描的目录路径（字符串或 Path 对象都行）

        Path() 会自动处理:
        - 字符串: Path("./some/dir")
        - 已经是 Path: Path(Path("./some/dir")) → 不会出错
        """
        self.directory = Path(directory)

        # 验证目录是否存在
        if not self.directory.exists():
            raise FileNotFoundError(f"目录不存在: {self.directory}")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"不是目录: {self.directory}")

    def scan(self):
        """
        扫描所有 .py 文件，返回文件信息列表

        返回格式:
        [
            {
                "path": "01_basics.py",          # 相对路径（方便展示）
                "full_path": "/absolute/path.py", # 绝对路径（方便读取）
                "size_kb": 3.5,                   # 文件大小
                "lines": 120                      # 代码行数
            },
            ...
        ]

        rglob("*.py") = 递归搜索所有 .py 文件（包括子目录）
        JS 类比: glob.sync('**/*.py')
        """
        files = []

        for file_path in sorted(self.directory.rglob("*.py")):
            # 跳过 __pycache__ 和隐藏目录里的文件
            # any() = JS 的 some()，parts 是路径的每一段
            # 比如 "a/__pycache__/b.py" → parts = ("a", "__pycache__", "b.py")
            if any(part.startswith(("__", ".")) for part in file_path.parts):
                continue

            # stat() 获取文件信息（大小、修改时间等）
            # JS 类比: fs.statSync(path)
            stat = file_path.stat()

            # relative_to() = 获取相对路径
            # JS 类比: path.relative(directory, filePath)
            files.append({
                "path": str(file_path.relative_to(self.directory)),
                "full_path": str(file_path),
                "size_kb": round(stat.st_size / 1024, 2),
                "lines": self._count_lines(file_path),
            })

        return files

    def read_file(self, file_path):
        """
        读取文件内容，返回字符串

        encoding="utf-8" 很重要：
        - Windows 默认编码是 GBK，不指定的话中文注释会乱码
        - JS 的 fs.readFileSync(path, 'utf-8') 也是同理
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _count_lines(self, file_path):
        """
        统计文件行数

        方法名前面加 _ 表示"内部方法，外部不要直接调用"
        JS 类比: 类似于 #privateMethods（私有方法）
        Python 没有真正的私有，_ 只是约定

        用 sum(1 for ...) 生成器而不是 readlines()
        因为生成器逐行读取，不会把整个文件加载到内存
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def get_summary(self, files=None):
        """
        打印扫描摘要

        参数:
            files: 文件列表（如果已经扫描过就传进来，避免重复扫描）
        """
        if files is None:
            files = self.scan()

        total_lines = sum(f["lines"] for f in files)
        total_size = sum(f["size_kb"] for f in files)

        print(f"📁 扫描目录: {self.directory}")
        print(f"📄 文件数量: {len(files)}")
        print(f"📝 总代码行数: {total_lines}")
        print(f"💾 总大小: {total_size:.2f} KB")

        return {
            "total_files": len(files),
            "total_lines": total_lines,
            "total_size_kb": round(total_size, 2),
        }
