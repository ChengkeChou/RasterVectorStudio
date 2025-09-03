"""
项目路径管理器
==============

这个模块提供了一个集中的、健壮的方式来管理项目中的所有路径。
无论用户从哪个目录启动程序，这些路径都会正确工作。

核心思想：所有路径都基于项目文件的实际位置来动态计算，
而不依赖于用户启动程序时的"工作目录"。
"""

from pathlib import Path
import sys
import os


def is_frozen():
    """检测是否运行在打包环境中"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_resource_path(relative_path):
    """获取资源文件路径，兼容开发环境和打包环境"""
    if is_frozen():
        # 在PyInstaller打包环境中
        base_path = Path(sys._MEIPASS)
    else:
        # 在开发环境中
        base_path = Path(__file__).parent.parent.parent
    
    return base_path / relative_path


class ProjectPaths:
    """项目路径管理器"""
    
    def __init__(self):
        # 项目根目录：兼容开发环境和打包环境
        if is_frozen():
            # 在打包环境中，使用临时目录
            self.PROJECT_ROOT = Path(sys._MEIPASS)
        else:
            # 在开发环境中，paths.py 在 src/config/ 下，所以 parent.parent 就是项目根
            self.PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
        
        # 核心目录
        self.SRC_DIR = self.PROJECT_ROOT / "src"
        self.BIN_DIR = self.PROJECT_ROOT / "bin"
        self.ENGINES_DIR = self.PROJECT_ROOT / "engines"  # 新增：engines目录
        self.WEB_DIR = self.PROJECT_ROOT / "web"
        self.RESOURCES_DIR = self.PROJECT_ROOT / "resources"
        
        # 外部工具可执行文件
        self.POTRACE_EXE = self._find_potrace()
        self.MKBITMAP_EXE = self._find_mkbitmap()
        self.TRACE_EXE = self._find_trace()
        self.TRACEGUI_EXE = self._find_tracegui()
        self.VTRACER_EXE = self._find_vtracer()
        
        # Web编辑器文件
        self.EDITOR_HTML = self.WEB_DIR / "editor.html"
        
        # 样式文件
        self.STYLES_QSS = self.SRC_DIR / "gui" / "styles.qss"
    
    def _find_potrace(self):
        """查找 potrace.exe"""
        possible_paths = [
            self.ENGINES_DIR / "potrace.exe",  # 第一优先级
            self.PROJECT_ROOT / "potrace-1.16.win64" / "potrace.exe",
            self.BIN_DIR / "potrace.exe",
            self.PROJECT_ROOT / "potrace.exe",
        ]
        for path in possible_paths:
            if path.exists():
                return path.resolve()
        return None
    
    def _find_mkbitmap(self):
        """查找 mkbitmap.exe"""
        possible_paths = [
            self.ENGINES_DIR / "mkbitmap.exe",  # 第一优先级
            self.PROJECT_ROOT / "potrace-1.16.win64" / "mkbitmap.exe",
            self.BIN_DIR / "mkbitmap.exe",
            self.PROJECT_ROOT / "mkbitmap.exe",
        ]
        for path in possible_paths:
            if path.exists():
                return path.resolve()
        return None
    
    def _find_trace(self):
        """查找 Trace(.NET) 可执行文件"""
        possible_paths = [
            self.ENGINES_DIR / "trace" / "Trace.exe",  # 第一优先级
            self.ENGINES_DIR / "Trace.exe",
            self.BIN_DIR / "trace.exe",
            self.BIN_DIR / "Trace.exe",
            self.PROJECT_ROOT / "trace.exe",
            self.PROJECT_ROOT / "Trace.exe",
        ]
        for path in possible_paths:
            if path.exists():
                return path.resolve()
        return None
    
    def _find_tracegui(self):
        """查找 TraceGui.exe"""
        possible_paths = [
            self.ENGINES_DIR / "tracegui" / "TraceGui.exe",  # 第一优先级
            self.ENGINES_DIR / "TraceGui.exe",
            self.BIN_DIR / "TraceGui.exe",
            self.PROJECT_ROOT / "TraceGui.exe",
        ]
        for path in possible_paths:
            if path.exists():
                return path.resolve()
        return None
    
    def _find_vtracer(self):
        """查找 vtracer 可执行文件"""
        possible_paths = [
            self.ENGINES_DIR / "vtracer.exe",  # 第一优先级
            self.ENGINES_DIR / "vtracer" / "vtracer.exe",
            self.PROJECT_ROOT / "vtracer-0.6.4" / "vtracer-0.6.4" / "target" / "release" / "vtracer.exe",
            self.BIN_DIR / "vtracer.exe",
            self.PROJECT_ROOT / "vtracer.exe",
        ]
        for path in possible_paths:
            if path.exists():
                return path.resolve()
        return None
    
    def ensure_project_root_in_path(self):
        """确保项目根目录在 sys.path 中，用于绝对导入"""
        project_root_str = str(self.PROJECT_ROOT)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
    
    def get_tool_info(self):
        """获取所有工具的可用性信息"""
        tools = {
            "potrace": self.POTRACE_EXE,
            "mkbitmap": self.MKBITMAP_EXE,
            "trace": self.TRACE_EXE,
            "tracegui": self.TRACEGUI_EXE,
            "vtracer": self.VTRACER_EXE,
        }
        
        info = {}
        for name, path in tools.items():
            info[name] = {
                "available": path is not None and path.exists(),
                "path": str(path) if path else "未找到"
            }
        
        return info
    
    def __str__(self):
        """返回路径信息的字符串表示"""
        lines = [
            f"项目根目录: {self.PROJECT_ROOT}",
            f"源码目录: {self.SRC_DIR}",
            f"工具目录: {self.BIN_DIR}",
            "",
            "外部工具:"
        ]
        
        for name, info in self.get_tool_info().items():
            status = "✅" if info["available"] else "❌"
            lines.append(f"  {status} {name}: {info['path']}")
        
        return "\n".join(lines)


# 创建全局实例
paths = ProjectPaths()

# 自动确保项目根目录在 sys.path 中
paths.ensure_project_root_in_path()


# 便捷函数
def get_potrace_path():
    """获取 potrace.exe 的绝对路径"""
    return paths.POTRACE_EXE

def get_mkbitmap_path():
    """获取 mkbitmap.exe 的绝对路径"""
    return paths.MKBITMAP_EXE

def get_trace_path():
    """获取 Trace 可执行文件的绝对路径"""
    return paths.TRACE_EXE

def get_tracegui_path():
    """获取 TraceGui.exe 的绝对路径"""
    return paths.TRACEGUI_EXE

def get_vtracer_path():
    """获取 vtracer 可执行文件的绝对路径"""
    return paths.VTRACER_EXE

def get_project_root():
    """获取项目根目录"""
    return paths.PROJECT_ROOT

def get_web_editor_path():
    """获取 Web 编辑器 HTML 文件路径"""
    return paths.EDITOR_HTML


if __name__ == "__main__":
    # 测试和调试信息
    print("=" * 50)
    print("项目路径管理器 - 调试信息")
    print("=" * 50)
    print(paths)
    print()
    print("当前工作目录:", Path.cwd())
    print("Python 解释器路径:", sys.executable)
