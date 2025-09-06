import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, Qt

def check_python_version():
    """检查Python版本"""
    if sys.version_info >= (3, 12):
        print(f"✅ 使用Python {sys.version.split()[0]} (Python 3.12兼容)")
        return True
    elif sys.version_info >= (3, 8):
        print(f"✅ 使用Python {sys.version.split()[0]}")
        return True
    else:
        print(f"❌ Python版本过低: {sys.version.split()[0]}")
        print("需要Python 3.8或更高版本")
        return False

def setup_environment():
    """设置环境变量"""
    # 解决OpenMP库冲突
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    print("🔧 环境变量已设置: KMP_DUPLICATE_LIB_OK=TRUE")

def check_diffvg_support():
    """检查DiffVG支持"""
    try:
        project_root = Path(__file__).parent.resolve()
        diffvg_path = project_root / "third_party" / "diffvg"
        
        if str(diffvg_path) not in sys.path:
            sys.path.insert(0, str(diffvg_path))
        
        import diffvg
        func_count = len([x for x in dir(diffvg) if not x.startswith('_')])
        
        if sys.version_info >= (3, 12):
            print(f"✅ DiffVG Python 3.12版本可用 ({func_count}个功能)")
        else:
            print(f"✅ DiffVG可用 ({func_count}个功能)")
        
        # 检查PyTorch支持
        try:
            import torch
            print("✅ PyTorch支持已启用")
        except ImportError:
            print("ℹ️ PyTorch未安装，使用CPU模式")
        
        return True
        
    except ImportError:
        print("⚠️ DiffVG不可用，将使用其他矢量化引擎")
        return False


def main():
    print("🚀 启动 RasterVectorStudio")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 设置环境
    setup_environment()
    
    # 检查DiffVG支持
    check_diffvg_support()
    
    print("\n🎨 初始化应用...")
    
    # 采用"提前导入 QWebEngineWidgets"的方式（与你之前的成功方式一致）
    try:
        # 在创建 QApplication 之前导入，以初始化 WebEngine 所需环境
        from PyQt5 import QtWebEngineWidgets  # noqa: F401
        print("✅ WebEngine支持已加载")
    except Exception:
        # 某些环境未安装 WebEngine，允许继续（编辑器里会降级）
        print("⚠️ WebEngine不可用，编辑功能可能受限")

    # 将项目根目录加入路径，以便通过 'src.' 前缀进行绝对导入
    project_root = Path(__file__).parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 确保工作目录为项目根目录
    os.chdir(project_root)

    print("🔧 创建QApplication...")
    # 必须在导入任何 Qt 组件之前创建 QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("RasterVectorStudio")
    app.setApplicationDisplayName("RasterVectorStudio - 位图转矢量与本地SVG编辑")
    
    if sys.version_info >= (3, 12):
        app.setApplicationVersion("1.0.0-py312")
    else:
        app.setApplicationVersion("1.0.0")
    
    print("✅ QApplication创建成功!")

    print("📦 导入主窗口...")
    from src.gui.main_window import MainWindow
    print("✅ 主窗口导入成功!")

    print("🏠 创建主窗口...")
    win = MainWindow()
    
    # --- 关键修改：连接应用退出清理信号 ---
    app.aboutToQuit.connect(win.cleanup)
    
    win.resize(1400, 900)
    win.show()
    print("✅ 主窗口创建并显示成功!")
    
    if sys.version_info >= (3, 12):
        print("🎉 RasterVectorStudio Python 3.12版本启动完成!")
    else:
        print("🎉 RasterVectorStudio启动完成!")
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
