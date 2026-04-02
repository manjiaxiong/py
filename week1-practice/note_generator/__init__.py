# __init__.py 的作用：告诉 Python 这个文件夹是一个"包（package）"
# 没有这个文件，Python 不会把这个目录当作模块来导入
# JS 类比：类似于 index.js，是包的入口文件
#
# 这里用 __init__.py 统一导出，外部只需要:
#   from note_generator import Config, Scanner, NoteGenerator
# 而不用:
#   from note_generator.config import Config
#   from note_generator.scanner import Scanner
#   ...

from .config import Config
from .scanner import Scanner
from .generator import NoteGenerator
