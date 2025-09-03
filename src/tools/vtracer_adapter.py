from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional


class VTracerAdapter:
    """调用 vtracer 可执行文件，将位图转换为 SVG 文本。"""

    def __init__(self):
        # 使用新的路径管理器
        from src.config.paths import get_vtracer_path
        
        vtracer_path = get_vtracer_path()
        
        if vtracer_path and vtracer_path.exists():
            self.vtracer = str(vtracer_path)
        else:
            # 尝试从PATH中查找
            vtracer_from_path = shutil.which("vtracer")
            if vtracer_from_path:
                self.vtracer = vtracer_from_path
            else:
                raise RuntimeError("vtracer 未找到。请确保已安装 vtracer 工具或将其放在项目目录中。")

    def run(
        self,
        input_path: Path,
        colormode: str = "color",
        mode: str = "spline",
        filter_speckle: int = 4,
        path_precision: int = 8,
    ) -> str:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(input_path)

        with TemporaryDirectory() as td:
            out_svg = Path(td) / "out.svg"
            cmd = [
                self.vtracer,
                "--input",
                str(input_path),
                "--output",
                str(out_svg),
                "--colormode",
                colormode,
                "--mode",
                mode,
                "--filter_speckle",
                str(filter_speckle),
                "--path_precision",
                str(path_precision),
            ]
            self._run(cmd, "vtracer 执行失败")
            return out_svg.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def _run(cmd: list[str], err: str):
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors='ignore') if e.stderr else ''
            stdout = e.stdout.decode(errors='ignore') if e.stdout else ''
            raise RuntimeError(f"{err}: {stderr or stdout}")
