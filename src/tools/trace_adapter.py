import subprocess
from pathlib import Path


class TraceAdapter:
    """调用 .NET 版 Trace 可执行文件（BitmapToVector）"""
    
    def __init__(self):
        # 使用新的路径管理器
        from src.config.paths import get_trace_path
        
        self.trace_exe = get_trace_path()
        
        # 检查工具可用性
        if not self.trace_exe or not self.trace_exe.exists():
            # 如果找不到，尝试使用PATH中的版本
            self.trace_exe = "Trace.exe"

    def run(self, input_path: Path) -> str:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        exe = str(self.trace_exe)

        # Trace.exe 的用法: Trace.exe <input> [output]
        # 如果不指定输出，它会自动生成 input.svg
        output_path = input_path.parent / f"{input_path.stem}.svg"

        cmd = [exe, str(input_path), str(output_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            error_msg = proc.stderr or proc.stdout
            raise RuntimeError(f"Trace 执行失败: {error_msg}")

        # 检查输出文件是否生成
        if output_path.exists():
            svg_content = output_path.read_text(encoding='utf-8')
            # 清理临时文件
            try:
                output_path.unlink()
            except:
                pass
            return svg_content
        else:
            raise RuntimeError(f"Trace 没有生成输出文件: {output_path}")
