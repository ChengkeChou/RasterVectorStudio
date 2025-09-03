from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebChannel import QWebChannel
from ..config.paths import get_resource_path


class SvgEditorWidget(QWidget):
    """本地 svgcanvas 编辑器：通过 QWebEngineView 加载 web/editor.html
    暴露 load_svg/get_svg 两个方法
    """
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.view = None  # 延迟初始化
        self.main_window = main_window  # 保存MainWindow引用以便通信
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self._svg_text: str = ""
        self._ready: bool = False

        # 注意：不再在这里调用 _init_web_view()
        # 将在 MainWindow 中 QApplication 创建后调用

    def init_web_view(self):
        """公共方法：在QApplication创建后初始化Web视图"""
        if self.view is None:
            self._init_web_view()

    def _init_web_view(self):
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtCore import QUrl
        
        self.view = QWebEngineView(self)
        self.lay.addWidget(self.view)
        
        # 设置WebChannel以便与JavaScript通信
        if self.main_window:
            self.channel = QWebChannel(self.view.page())
            self.view.page().setWebChannel(self.channel)
            # 将MainWindow实例注册到channel，让JS可以调用它的方法
            self.channel.registerObject("backend", self.main_window)
        
        # 加载专业版Paper.js编辑器页面
        html_path = get_resource_path("web/paperjs_editor_pro.html")
        self.view.load(QUrl.fromLocalFile(str(html_path)))
        self.view.loadFinished.connect(self._on_loaded)

    def _on_loaded(self, ok: bool):
        self._ready = bool(ok)
        if self._ready and self._svg_text and self.view:
            # 页面就绪后使用Paper.js的API加载SVG
            script = f"window.loadSvg && window.loadSvg(`{self._escape_js(self._svg_text)}`);"
            self.view.page().runJavaScript(script)

    def load_svg(self, svg: str):
        self._svg_text = svg or ""
        # 使用Paper.js API注入SVG内容
        if self._ready and self.view:
            script = f"window.loadSvg && window.loadSvg(`{self._escape_js(self._svg_text)}`);"
            self.view.page().runJavaScript(script)

    def get_svg(self) -> str:
        # 使用Paper.js API从前端获取当前SVG内容
        if self._ready and self.view:
            try:
                # 使用Paper.js的导出API
                script = "window.getSvg ? window.getSvg() : '';"
                
                # 使用回调方式处理异步结果
                def handle_result(result):
                    if result is not None:
                        svg_content = str(result)
                        if svg_content and svg_content != "''":
                            self._svg_text = svg_content
                
                self.view.page().runJavaScript(script, handle_result)
                
            except Exception as e:
                print(f"获取SVG失败: {e}")
        
        # 返回缓存的内容
        return self._svg_text
    
    def get_svg_content(self) -> str:
        """获取SVG内容的便捷方法"""
        return self.get_svg()
    
    def set_svg_content(self, svg: str):
        """设置SVG内容的便捷方法"""
        self.load_svg(svg)
        
    def get_svg_async(self, callback):
        """异步获取SVG内容"""
        if self._ready and self.view:
            script = "window.getSvg ? window.getSvg() : '';"
            self.view.page().runJavaScript(script, callback)
        else:
            callback(self._svg_text)
    
    def set_svg_async(self, svg: str, callback=None):
        """异步设置SVG内容"""
        self._svg_text = svg or ""
        if self._ready and self.view:
            script = f"window.loadSvg && window.loadSvg(`{self._escape_js(self._svg_text)}`);"
            if callback:
                self.view.page().runJavaScript(script, callback)
            else:
                self.view.page().runJavaScript(script)
        elif callback:
            callback(True)
    
    def set_tool(self, tool_name: str):
        """设置当前工具"""
        if self._ready and self.view:
            script = f"window.activateTool && window.activateTool('{tool_name}');"
            self.view.page().runJavaScript(script)
            print(f"工具切换到: {tool_name}")
        else:
            print(f"编辑器未就绪，缓存工具: {tool_name}")
    
    def set_current_color(self, color: str):
        """设置当前颜色"""
        if self._ready and self.view:
            script = f"window.setCurrentColor && window.setCurrentColor('{color}');"
            self.view.page().runJavaScript(script)
            print(f"颜色设置为: {color}")
    
    def set_color(self, color: str):
        """设置当前颜色 (兼容方法)"""
        self.set_current_color(color)
    
    def set_stroke_width(self, width: int):
        """设置描边宽度"""
        if self._ready and self.view:
            script = f"window.setStrokeWidth && window.setStrokeWidth({width});"
            self.view.page().runJavaScript(script)
            print(f"描边宽度设置为: {width}")
    
    def apply_color_to_selected(self, color: str, mode: str = "fill", callback=None):
        """对选中元素应用颜色"""
        if self._ready and self.view:
            # 先设置颜色
            self.set_current_color(color)
            # 然后切换到填充工具进行应用 (模拟点击操作)
            if mode == "fill":
                self.set_tool("fill")
            
            if callback:
                callback(True)
            print(f"应用颜色 {color} 到选中元素 ({mode})")
            return True
        
        if callback:
            callback(False)
        return False
    
    def get_selected_elements(self, callback):
        """获取选中元素信息"""
        if self._ready and self.view:
            script = """
            (function() {
                var selected = [];
                if (paper.project && paper.project.activeLayer) {
                    paper.project.activeLayer.children.forEach(function(item, index) {
                        if (item.selected) {
                            selected.push({
                                id: item.id || 'item_' + index,
                                type: item.className,
                                bounds: item.bounds ? {
                                    x: item.bounds.x,
                                    y: item.bounds.y,
                                    width: item.bounds.width,
                                    height: item.bounds.height
                                } : null
                            });
                        }
                    });
                }
                return selected;
            })();
            """
            self.view.page().runJavaScript(script, callback)
        else:
            callback([])

    def clear_selection(self):
        """清除选择"""
        if self._ready and self.view:
            script = "paper.project && paper.project.deselectAll && paper.project.deselectAll();"
            self.view.page().runJavaScript(script)
    
    def run_javascript(self, script):
        """执行JavaScript代码"""
        if self._ready and self.view:
            self.view.page().runJavaScript(script)
    
    
    def run_javascript(self, script):
        """执行JavaScript代码"""
        if self._ready and self.view:
            self.view.page().runJavaScript(script)

    @staticmethod
    def _escape_js(s: str) -> str:
        return s.replace("`", "\\`")
