import subprocess
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional


class PotracePipeline:
    """使用 mkbitmap + potrace 将位图转为 SVG。
    将处理过程拆分为独立的步骤，便于调试和控制。
    """
    def __init__(self):
        # 使用新的路径管理器
        from src.config.paths import get_potrace_path, get_mkbitmap_path
        
        self.potrace_exe = get_potrace_path()
        self.mkbitmap_exe = get_mkbitmap_path()
        
        # 检查工具可用性
        if not self.potrace_exe or not self.potrace_exe.exists():
            raise RuntimeError(f"potrace.exe 未找到。请确保已安装 potrace 工具。")
        if not self.mkbitmap_exe or not self.mkbitmap_exe.exists():
            raise RuntimeError(f"mkbitmap.exe 未找到。请确保已安装 mkbitmap 工具。")

    def run(self, input_path: Path, threshold: int = 128, turdsize: int = 2,
            alphamax: float = 1.0, edge_mode: bool = False, debug: bool = False,
            filter_radius: int = 4, scale_factor: int = 2, blur_radius: float = 0.0,
            turnpolicy: str = "minority", opttolerance: float = 0.2, unit: int = 10,
            invert: bool = False, longcurve: bool = False) -> str:
        """运行完整的mkbitmap+potrace管道"""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        with TemporaryDirectory() as td:
            tmp = Path(td)

            # 步骤1: 预处理图像为位图
            pbm_path = self._run_mkbitmap(input_path, tmp, threshold, debug, 
                                        filter_radius, scale_factor, blur_radius, invert)

            # 步骤2: 位图转SVG
            svg_content = self._run_potrace(pbm_path, tmp, turdsize, alphamax, edge_mode, debug,
                                          turnpolicy, opttolerance, unit, longcurve)

            return svg_content

    def _run_mkbitmap(self, input_path: Path, tmp_dir: Path, threshold: int, debug: bool,
                     filter_radius: int = 4, scale_factor: int = 2, blur_radius: float = 0.0,
                     invert: bool = False) -> Path:
        """运行mkbitmap进行图像预处理"""
        print(f"步骤1: 运行mkbitmap处理 {input_path.name}")

        # 检查输入格式
        supported = {".pnm", ".pbm", ".pgm", ".ppm", ".bmp"}
        src_for_mk = input_path

        if input_path.suffix.lower() not in supported:
            print(f"输入格式{input_path.suffix}不受支持，转换为BMP...")
            try:
                from PIL import Image
                img = Image.open(input_path).convert("RGB")
                bmp_path = tmp_dir / "_mk_src.bmp"
                img.save(bmp_path, format="BMP")
                src_for_mk = bmp_path
                print(f"已转换为: {bmp_path}")
            except Exception as conv_err:
                raise RuntimeError(f"无法将输入转换为BMP: {conv_err}")

        # 准备mkbitmap命令
        pbm_path = tmp_dir / "preprocessed.pbm"
        mkbitmap_exe = str(self.mkbitmap_exe)

        # mkbitmap参数:
        # -f: 高通滤波器半径
        # -s: 缩放因子（推荐用于potrace）
        # -t: 阈值 (0-1之间)
        # -3: 使用三次插值
        # -i: 反转输入
        # -b: 模糊半径
        threshold_normalized = threshold / 255.0  # 转换为0-1范围
        mk_cmd = [
            mkbitmap_exe,
            "-f", str(filter_radius),    # 高通滤波半径
            "-s", str(scale_factor),     # 缩放因子
            "-t", f"{threshold_normalized:.3f}",  # 阈值
            "-3",                        # 三次插值
        ]
        
        # 添加可选参数
        if invert:
            mk_cmd.append("-i")
        
        if blur_radius > 0:
            mk_cmd.extend(["-b", f"{blur_radius:.1f}"])
        
        mk_cmd.extend(["-o", str(pbm_path), str(src_for_mk)])

        if debug:
            print(f"mkbitmap命令: {' '.join(mk_cmd)}")

        try:
            result = subprocess.run(mk_cmd, check=True, capture_output=True, text=True)
            if debug:
                print("mkbitmap stdout:", result.stdout)
                if result.stderr:
                    print("mkbitmap stderr:", result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"mkbitmap执行失败: {e.returncode}"
            if e.stdout:
                error_msg += f"\nstdout: {e.stdout}"
            if e.stderr:
                error_msg += f"\nstderr: {e.stderr}"
            raise RuntimeError(error_msg)

        if not pbm_path.exists():
            raise RuntimeError("mkbitmap未生成输出文件")

        print(f"mkbitmap完成，输出: {pbm_path}")
        return pbm_path

    def _run_potrace(self, pbm_path: Path, tmp_dir: Path, turdsize: int,
                    alphamax: float, edge_mode: bool, debug: bool,
                    turnpolicy: str = "minority", opttolerance: float = 0.2, 
                    unit: int = 10, longcurve: bool = False) -> str:
        """运行potrace进行位图到SVG转换"""
        print(f"步骤2: 运行potrace处理 {pbm_path.name}")

        svg_path = tmp_dir / "output.svg"
        potrace_exe = str(self.potrace_exe)

        # potrace参数:
        # -s: SVG输出
        # -o: 输出文件
        # --turdsize: 抑制小斑点
        # --alphamax: 拐角阈值
        # --turnpolicy: 转向策略
        # --opttolerance: 优化容差
        # --unit: 单位量化
        # --longcurve: 禁用曲线优化
        po_cmd = [
            potrace_exe,
            str(pbm_path),
            "-s",  # SVG输出
            "-o", str(svg_path),
            "--turdsize", str(turdsize),
            "--alphamax", str(alphamax),
            "--turnpolicy", turnpolicy,
            "--opttolerance", str(opttolerance),
            "--unit", str(unit)
        ]
        
        # 添加可选参数
        if longcurve:
            po_cmd.append("--longcurve")

        if debug:
            print(f"potrace命令: {' '.join(po_cmd)}")

        try:
            result = subprocess.run(po_cmd, check=True, capture_output=True, text=True)
            if debug:
                print("potrace stdout:", result.stdout)
                if result.stderr:
                    print("potrace stderr:", result.stderr)
        except subprocess.CalledProcessError as e:
            error_msg = f"potrace执行失败: {e.returncode}"
            if e.stdout:
                error_msg += f"\nstdout: {e.stdout}"
            if e.stderr:
                error_msg += f"\nstderr: {e.stderr}"
            raise RuntimeError(error_msg)

        if not svg_path.exists():
            raise RuntimeError("potrace未生成输出文件")

        # 读取SVG内容
        try:
            svg_content = svg_path.read_text(encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"无法读取SVG文件: {e}")

        print(f"potrace完成，SVG大小: {len(svg_content)} 字符")

        # 处理边缘模式
        if edge_mode:
            svg_content = self._apply_edge_mode(svg_content, debug)

        return svg_content

    def _apply_edge_mode(self, svg: str, debug: bool) -> str:
        """应用边缘模式：将填充路径改为描边"""
        original_svg = svg

        # 替换黑色填充为描边
        svg = svg.replace('fill="black"', 'fill="none" stroke="#000" stroke-width="1"')
        svg = svg.replace('fill="#000000"', 'fill="none" stroke="#000" stroke-width="1"')

        # 移除重复的stroke属性
        import re
        # 移除多余的 stroke="none"
        svg = re.sub(r'\s*stroke="none"', '', svg)
        # 移除重复的stroke属性，保留第一个
        svg = re.sub(r'(stroke="#\w+"\s+stroke-width="\d+"\s+)stroke="#\w+"\s+stroke-width="\d+"', r'\1', svg)

        # 确保<g>元素有正确的描边设置
        if '<g ' in svg and 'fill="none"' in svg and 'stroke=' not in svg:
            svg = svg.replace('<g ', '<g stroke="#000" stroke-width="1" ')

        if debug and svg != original_svg:
            print("已应用边缘模式处理")

        return svg

    def run_mkbitmap_only(self, input_path: Path, output_path: Path,
                         threshold: int = 128, debug: bool = False,
                         filter_radius: int = 4, scale_factor: int = 2, 
                         blur_radius: float = 0.0, invert: bool = False) -> Path:
        """仅运行mkbitmap步骤，返回PBM文件路径"""
        input_path = Path(input_path)
        output_path = Path(output_path)

        with TemporaryDirectory() as td:
            tmp = Path(td)
            pbm_path = self._run_mkbitmap(input_path, tmp, threshold, debug,
                                        filter_radius, scale_factor, blur_radius, invert)

            # 复制到目标位置
            shutil.copy2(pbm_path, output_path)
            print(f"PBM文件已保存到: {output_path}")
            return output_path

    def run_potrace_only(self, input_path: Path, turdsize: int = 2,
                        alphamax: float = 1.0, edge_mode: bool = False,
                        debug: bool = False, turnpolicy: str = "minority", 
                        opttolerance: float = 0.2, unit: int = 10, 
                        longcurve: bool = False) -> str:
        """仅运行potrace步骤，自动处理格式转换"""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        with TemporaryDirectory() as td:
            tmp = Path(td)
            
            # 检查输入文件格式
            potrace_supported = {".pbm", ".pgm", ".ppm", ".bmp"}
            
            if input_path.suffix.lower() in potrace_supported:
                # 如果已经是potrace支持的格式，直接使用
                pbm_path = input_path
                if debug:
                    print(f"输入文件{input_path.name}已是potrace支持的格式")
            else:
                # 如果不是支持的格式，先转换
                print(f"输入格式{input_path.suffix}不受potrace直接支持，正在转换为PBM...")
                try:
                    from PIL import Image
                    
                    # 加载图像
                    img = Image.open(input_path)
                    
                    # 转换为RGB模式（确保兼容性）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # 有透明度或调色板的图像，转换为RGB
                        img = img.convert('RGB')
                    elif img.mode != 'RGB' and img.mode != 'L':
                        img = img.convert('RGB')
                    
                    # 转换为灰度
                    if img.mode != 'L':
                        img = img.convert('L')
                    
                    # 简单二值化处理 (使用阈值128)
                    import numpy as np
                    img_array = np.array(img)
                    # 二值化：大于128的设为255(白色)，小于等于128的设为0(黑色)
                    binary_array = np.where(img_array > 128, 255, 0).astype(np.uint8)
                    binary_img = Image.fromarray(binary_array, mode='L')
                    
                    # 保存为PBM格式 (使用单色模式)
                    pbm_path = tmp / "converted.pbm"
                    # 转换为单色模式以获得真正的PBM
                    binary_img = binary_img.convert('1')  # 转换为1位单色
                    binary_img.save(pbm_path, format="PPM")  # 保存为PPM格式（PIL的PBM支持有限）
                    
                    if debug:
                        print(f"已转换为PBM格式: {pbm_path}")
                        print(f"转换后文件大小: {pbm_path.stat().st_size} 字节")
                    
                except Exception as conv_err:
                    raise RuntimeError(f"无法转换输入文件为PBM格式: {conv_err}")
            
            return self._run_potrace(pbm_path, tmp, turdsize, alphamax, edge_mode, debug,
                                   turnpolicy, opttolerance, unit, longcurve)
