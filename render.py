"""
共享的终端渲染原语，供 commands / permissions / hooks 复用，只依赖 rich。
抽到这里是为了打破 commands 与 permissions/hooks 的循环依赖，调用方就能在文件顶部直接 import。
"""
from rich.console import Console
from rich.padding import Padding


# 共享的 Console 实例，跨平台自动处理 ANSI 颜色（Windows 老终端也能正常显示）。
# highlight=False 关闭 Rich 自带的数字/字符串自动高亮，只让我们手动加的 markup 生效。
console = Console(highlight=False)


def print_step(label: str, content: str = "") -> None:
    """
    打印一个中间过程 block：标签独占一行，内容用 Padding 左缩进 2 格
    （这样自动折行的续行也能保持缩进），末尾留一个空行。
    """
    console.print(label)
    if content:
        console.print(Padding(content, (0, 0, 0, 2)))
    console.print()
