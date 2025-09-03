import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, Qt


def main():
    # 采用"提前导入 QWebEngineWidgets"的方式（与你之前的成功方式一致）
    try:
        # 在创建 QApplication 之前导入，以初始化 WebEngine 所需环境
        from PyQt5 import QtWebEngineWidgets  # noqa: F401
    except Exception:
        # 某些环境未安装 WebEngine，允许继续（编辑器里会降级）
        pass

    # 将项目根目录加入路径，以便通过 'src.' 前缀进行绝对导入
    project_root = Path(__file__).parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 确保工作目录为项目根目录
    os.chdir(project_root)

    print("Creating QApplication...")
    # 必须在导入任何 Qt 组件之前创建 QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("RasterVectorStudio")
    app.setApplicationDisplayName("RasterVectorStudio - 位图转矢量与本地SVG编辑")
    app.setApplicationVersion("0.1.0")
    print("QApplication created successfully!")

    print("Importing MainWindow...")
    from src.gui.main_window import MainWindow
    print("MainWindow imported successfully!")

    print("Creating MainWindow...")
    win = MainWindow()
    
    # --- 关键修改：连接应用退出清理信号 ---
    app.aboutToQuit.connect(win.cleanup)
    
    win.resize(1400, 900)
    win.show()
    print("MainWindow created and shown!")
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
