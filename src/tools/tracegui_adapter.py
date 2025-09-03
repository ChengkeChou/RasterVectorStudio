import subprocess
from pathlib import Path


class TraceGuiAdapter:
    """调用 TraceGui 可执行文件进行位图转矢量
    TraceGui 是一个基于 .NET 和 Avalonia 的图形界面工具，
    但也可以通过命令行调用进行批处理转换。
    """
    def __init__(self):
        # 使用新的路径管理器
        from src.config.paths import get_tracegui_path
        
        self.tracegui_exe = get_tracegui_path()
        
        # 检查工具可用性
        if not self.tracegui_exe or not self.tracegui_exe.exists():
            # 如果找不到，尝试使用PATH中的版本
            self.tracegui_exe = "TraceGui.exe"

    def run(self, input_path: Path, output_path: Path | None = None) -> str:
        """运行TraceGui进行转换

        Args:
            input_path: 输入图像文件路径
            output_path: 输出SVG文件路径，如果为None则使用默认名称

        Returns:
            SVG内容字符串
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        exe = str(self.tracegui_exe)

        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_trace.svg"

        output_path = Path(output_path)

        # TraceGui 的命令行参数
        # 通常格式: TraceGui.exe input.png output.svg [options]
        cmd = [exe, str(input_path), str(output_path)]

        try:
            # 运行TraceGui
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"TraceGui 执行失败: {error_msg}")

            # 检查输出文件是否存在
            if output_path.exists():
                return output_path.read_text(encoding='utf-8')
            else:
                # 如果没有生成文件，可能是输出到了标准输出
                return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError("TraceGui 执行超时")
        except Exception as e:
            raise RuntimeError(f"TraceGui 执行出错: {e}")
