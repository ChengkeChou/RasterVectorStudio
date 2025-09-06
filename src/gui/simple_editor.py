"""
简化版SVG编辑器 - 仅包含Paper.js核心功能
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import json
import os
from pathlib import Path

class SimpleEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_root = Path(__file__).parent.parent.parent
        self.setupUI()
        self.setupWebChannel()
        
    def setupUI(self):
        """设置用户界面"""
        self.setWindowTitle("RasterVectorStudio - Paper.js 编辑器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QHBoxLayout(central_widget)
        
        # 创建左侧工具面板
        self.createToolPanel(layout)
        
        # 创建Web视图
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, stretch=3)
        
        # 加载HTML文件
        html_path = self.project_root / "web" / "paperjs_editor.html"
        if html_path.exists():
            self.web_view.load(QUrl.fromLocalFile(str(html_path)))
            print(f"✓ 加载编辑器: {html_path}")
        else:
            print(f"❌ 编辑器文件不存在: {html_path}")
    
    def createToolPanel(self, parent_layout):
        """创建工具面板"""
        tool_panel = QVBoxLayout()
        
        # 工具选择
        tool_group = QGroupBox("工具")
        tool_layout = QVBoxLayout(tool_group)
        
        self.tool_buttons = {}
        tools = [
            ("select", "选择"),
            ("pen", "绘制"),
            ("rectangle", "矩形"),
            ("circle", "圆形"),
            ("text", "文本")
        ]
        
        for tool_id, tool_name in tools:
            btn = QPushButton(tool_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tool_id: self.setTool(t))
            self.tool_buttons[tool_id] = btn
            tool_layout.addWidget(btn)
        
        # 默认选择选择工具
        self.tool_buttons["select"].setChecked(True)
        
        tool_panel.addWidget(tool_group)
        
        # 颜色选择
        color_group = QGroupBox("颜色")
        color_layout = QVBoxLayout(color_group)
        
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.selectColor)
        self.color_button.setStyleSheet("background-color: #000000; color: white;")
        color_layout.addWidget(self.color_button)
        
        tool_panel.addWidget(color_group)
        
        # 文件操作
        file_group = QGroupBox("文件")
        file_layout = QVBoxLayout(file_group)
        
        load_btn = QPushButton("加载SVG")
        load_btn.clicked.connect(self.loadSvg)
        file_layout.addWidget(load_btn)
        
        save_btn = QPushButton("保存SVG")
        save_btn.clicked.connect(self.saveSvg)
        file_layout.addWidget(save_btn)
        
        tool_panel.addWidget(file_group)
        
        # 测试按钮
        test_group = QGroupBox("测试")
        test_layout = QVBoxLayout(test_group)
        
        test_btn = QPushButton("测试Paper.js")
        test_btn.clicked.connect(self.testPaperJs)
        test_layout.addWidget(test_btn)
        
        create_test_btn = QPushButton("创建测试图形")
        create_test_btn.clicked.connect(self.createTestShape)
        test_layout.addWidget(create_test_btn)
        
        tool_panel.addWidget(test_group)
        
        tool_panel.addStretch()
        
        # 创建工具面板容器
        tool_widget = QWidget()
        tool_widget.setLayout(tool_panel)
        tool_widget.setMaximumWidth(200)
        
        parent_layout.addWidget(tool_widget)
    
    def setupWebChannel(self):
        """设置Web通道"""
        self.channel = QWebChannel()
        self.channel.registerObject("pybridge", self)
        self.web_view.page().setWebChannel(self.channel)
    
    def setTool(self, tool_name):
        """设置当前工具"""
        # 更新按钮状态
        for tool_id, btn in self.tool_buttons.items():
            btn.setChecked(tool_id == tool_name)
        
        # 向Web页面发送工具切换命令
        script = f"if (typeof setTool !== 'undefined') setTool('{tool_name}');"
        self.web_view.page().runJavaScript(script)
        print(f"✓ 切换工具: {tool_name}")
    
    def selectColor(self):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.color_button.setStyleSheet(f"background-color: {color_hex}; color: white;")
            
            # 向Web页面发送颜色设置命令
            script = f"if (typeof setCurrentColor !== 'undefined') setCurrentColor('{color_hex}');"
            self.web_view.page().runJavaScript(script)
            print(f"✓ 设置颜色: {color_hex}")
    
    def loadSvg(self):
        """加载SVG文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择SVG文件", "", "SVG文件 (*.svg);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                
                # 转义SVG内容以便在JavaScript中使用
                svg_escaped = json.dumps(svg_content)
                script = f"if (typeof loadSvg !== 'undefined') loadSvg({svg_escaped});"
                self.web_view.page().runJavaScript(script)
                print(f"✓ 加载SVG: {file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载SVG失败: {e}")
    
    def saveSvg(self):
        """保存SVG文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存SVG文件", "", "SVG文件 (*.svg);;所有文件 (*)"
        )
        
        if file_path:
            # 从Web页面获取SVG内容
            def save_callback(svg_content):
                if svg_content:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(svg_content)
                        print(f"✓ 保存SVG: {file_path}")
                        QMessageBox.information(self, "成功", "SVG文件保存成功！")
                    except Exception as e:
                        QMessageBox.warning(self, "错误", f"保存SVG失败: {e}")
                else:
                    QMessageBox.warning(self, "错误", "无法获取SVG内容")
            
            script = "if (typeof getSvg !== 'undefined') getSvg(); else '';"
            self.web_view.page().runJavaScript(script, save_callback)
    
    def testPaperJs(self):
        """测试Paper.js功能"""
        test_script = """
        if (typeof paper !== 'undefined') {
            console.log('Paper.js 可用，版本:', paper.version);
            'Paper.js 工作正常！版本: ' + paper.version;
        } else {
            console.error('Paper.js 不可用');
            'Paper.js 不可用！';
        }
        """
        
        def test_callback(result):
            QMessageBox.information(self, "Paper.js 测试", result)
        
        self.web_view.page().runJavaScript(test_script, test_callback)
    
    def createTestShape(self):
        """创建测试图形"""
        test_script = """
        if (typeof paper !== 'undefined' && paper.project) {
            try {
                // 清除现有内容
                paper.project.clear();
                
                // 创建一个红色圆形
                var circle = new paper.Path.Circle(new paper.Point(100, 100), 50);
                circle.fillColor = 'red';
                circle.strokeColor = 'black';
                circle.strokeWidth = 2;
                
                // 创建一个蓝色矩形
                var rect = new paper.Path.Rectangle(new paper.Point(200, 50), new paper.Size(100, 100));
                rect.fillColor = 'blue';
                rect.strokeColor = 'black';
                rect.strokeWidth = 2;
                
                // 更新视图
                paper.view.draw();
                
                '测试图形创建成功！';
            } catch (error) {
                '创建测试图形失败: ' + error.message;
            }
        } else {
            'Paper.js 未正确初始化';
        }
        """
        
        def create_callback(result):
            QMessageBox.information(self, "创建测试图形", result)
            print(f"创建测试图形结果: {result}")
        
        self.web_view.page().runJavaScript(test_script, create_callback)
    
    @pyqtSlot(str)
    def onWebMessage(self, message):
        """处理来自Web页面的消息"""
        try:
            data = json.loads(message)
            print(f"收到Web消息: {data}")
        except:
            print(f"收到Web消息: {message}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        print("正在关闭编辑器...")
        event.accept()
