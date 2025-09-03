from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QSplitter
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt


class SimpleSvgViewer(QWidget):
    """简单的SVG查看器组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.svg_content = ""
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QHBoxLayout()

        self.load_btn = QPushButton("加载SVG")
        self.load_btn.clicked.connect(self.load_svg_file)
        toolbar.addWidget(self.load_btn)

        self.save_btn = QPushButton("保存SVG")
        self.save_btn.clicked.connect(self.save_svg_file)
        toolbar.addWidget(self.save_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # SVG显示区域
        self.svg_widget = QSvgWidget()
        self.svg_widget.setMinimumSize(400, 300)
        layout.addWidget(self.svg_widget)

        # 状态标签
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

    def load_svg_content(self, svg_content):
        """加载SVG内容"""
        try:
            self.svg_content = svg_content
            # 将SVG内容转换为字节数组并加载
            svg_bytes = svg_content.encode('utf-8')
            self.svg_widget.load(svg_bytes)
            self.status_label.setText(f"已加载SVG ({len(svg_content)} 字符)")
        except Exception as e:
            self.status_label.setText(f"加载SVG失败: {e}")

    def load_svg_file(self):
        """加载SVG文件"""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择SVG文件", "", "SVG文件 (*.svg);;所有文件 (*)"
        )
        if file_path:
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                self.load_svg_content(content)
            except Exception as e:
                self.status_label.setText(f"读取文件失败: {e}")

    def save_svg_file(self):
        """保存SVG文件"""
        if not self.svg_content:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "警告", "没有可保存的SVG内容")
            return

        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存SVG文件", "", "SVG文件 (*.svg);;所有文件 (*)"
        )
        if file_path:
            try:
                Path(file_path).write_text(self.svg_content, encoding='utf-8')
                self.status_label.setText(f"已保存: {file_path}")
            except Exception as e:
                self.status_label.setText(f"保存失败: {e}")

    def get_svg_content(self):
        """获取当前SVG内容"""
        return self.svg_content


class SimpleSvgEditor(QWidget):
    """简单的SVG文本编辑器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QHBoxLayout()

        self.apply_btn = QPushButton("应用更改")
        self.apply_btn.clicked.connect(self.apply_changes)
        toolbar.addWidget(self.apply_btn)

        self.format_btn = QPushButton("格式化")
        self.format_btn.clicked.connect(self.format_svg)
        toolbar.addWidget(self.format_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 分割器：左边文本编辑器，右边预览
        splitter = QSplitter()  # 默认水平分割

        # 文本编辑器
        self.text_editor = QTextEdit()
        self.text_editor.setFontFamily("Consolas")
        self.text_editor.setFontPointSize(10)
        splitter.addWidget(self.text_editor)

        # SVG预览
        self.svg_viewer = SimpleSvgViewer()
        splitter.addWidget(self.svg_viewer)

        # 设置分割器比例
        splitter.setSizes([400, 400])

        layout.addWidget(splitter)

        # 状态标签
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

    def set_svg_content(self, content):
        """设置SVG内容"""
        self.text_editor.setPlainText(content)
        self.svg_viewer.load_svg_content(content)

    def get_svg_content(self):
        """获取SVG内容"""
        return self.text_editor.toPlainText()

    def apply_changes(self):
        """应用文本编辑器的更改到预览"""
        content = self.get_svg_content()
        self.svg_viewer.load_svg_content(content)
        self.status_label.setText("已应用更改")

    def format_svg(self):
        """格式化SVG代码"""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom

            content = self.get_svg_content()
            if not content.strip():
                return

            # 解析并格式化
            root = ET.fromstring(content)
            rough_string = ET.tostring(root, encoding='unicode')
            parsed = minidom.parseString(rough_string)
            formatted = parsed.toprettyxml(indent="  ")

            # 移除空行
            lines = [line for line in formatted.split('\n') if line.strip()]
            formatted = '\n'.join(lines)

            self.text_editor.setPlainText(formatted)
            self.apply_changes()
            self.status_label.setText("已格式化SVG代码")

        except Exception as e:
            self.status_label.setText(f"格式化失败: {e}")


class SvgEditorTabs(QWidget):
    """SVG编辑器标签页组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        from PyQt5.QtWidgets import QTabWidget

        layout = QVBoxLayout(self)

        # 创建标签页
        self.tabs = QTabWidget()

        # 简单查看器标签页
        self.viewer_tab = SimpleSvgViewer()
        self.tabs.addTab(self.viewer_tab, "SVG查看器")

        # 文本编辑器标签页
        self.editor_tab = SimpleSvgEditor()
        self.tabs.addTab(self.editor_tab, "文本编辑器")

        # Web编辑器标签页（如果可用）
        try:
            from src.gui.editor_widget import SvgEditorWidget
            self.web_editor_tab = SvgEditorWidget()
            self.tabs.addTab(self.web_editor_tab, "Web编辑器")
            self.has_web_editor = True
        except Exception as e:
            print(f"Web编辑器不可用: {e}")
            self.has_web_editor = False

        layout.addWidget(self.tabs)

    def load_svg(self, svg_content):
        """加载SVG内容到所有编辑器"""
        self.viewer_tab.load_svg_content(svg_content)
        self.editor_tab.set_svg_content(svg_content)
        if self.has_web_editor:
            self.web_editor_tab.load_svg(svg_content)

    def get_svg(self):
        """从当前活动编辑器获取SVG内容"""
        current_index = self.tabs.currentIndex()
        if current_index == 0:  # 查看器
            return self.viewer_tab.get_svg_content()
        elif current_index == 1:  # 文本编辑器
            return self.editor_tab.get_svg_content()
        elif current_index == 2 and self.has_web_editor:  # Web编辑器
            return self.web_editor_tab.get_svg()
        return ""
