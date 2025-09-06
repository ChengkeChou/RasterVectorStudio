#!/usr/bin/env python3
"""
WebChannel 接口 - 专门用于与 JavaScript 通信
只暴露必要的方法，避免大量属性警告
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class WebChannelInterface(QObject):
    """WebChannel 接口类，只暴露必要的方法给 JavaScript"""
    
    # 信号
    svg_updated = pyqtSignal(str)  # SVG 更新信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
    
    @pyqtSlot(str)
    def update_svg(self, svg_content):
        """从 JavaScript 接收 SVG 更新"""
        try:
            if self.main_window and hasattr(self.main_window, 'update_svg_display'):
                self.main_window.update_svg_display(svg_content)
        except Exception as e:
            print(f"SVG 更新失败: {e}")
    
    @pyqtSlot(str)
    def save_svg(self, svg_content):
        """保存 SVG 文件"""
        try:
            if self.main_window and hasattr(self.main_window, 'save_svg_file'):
                self.main_window.save_svg_file(svg_content)
        except Exception as e:
            print(f"SVG 保存失败: {e}")
    
    @pyqtSlot(str)
    def export_svg(self, svg_content):
        """导出 SVG 文件"""
        try:
            if self.main_window and hasattr(self.main_window, 'export_svg_file'):
                self.main_window.export_svg_file(svg_content)
        except Exception as e:
            print(f"SVG 导出失败: {e}")
    
    @pyqtSlot(str)
    def log_message(self, message):
        """记录来自 JavaScript 的消息"""
        print(f"JS: {message}")
    
    @pyqtSlot(str)
    def on_editor_ready(self, message):
        """编辑器就绪回调"""
        print(f"编辑器就绪: {message}")
        if self.main_window and hasattr(self.main_window, 'on_editor_ready'):
            self.main_window.on_editor_ready()
    
    @pyqtSlot(str, result=str)
    def get_config(self, key):
        """获取配置值"""
        try:
            if self.main_window and hasattr(self.main_window, 'get_config'):
                return str(self.main_window.get_config(key, ""))
            return ""
        except Exception as e:
            print(f"获取配置失败: {e}")
            return ""
    
    @pyqtSlot(str, str)
    def set_config(self, key, value):
        """设置配置值"""
        try:
            if self.main_window and hasattr(self.main_window, 'set_config'):
                self.main_window.set_config(key, value)
        except Exception as e:
            print(f"设置配置失败: {e}")
    
    @pyqtSlot(result=str)
    def get_current_svg(self):
        """获取当前 SVG 内容"""
        try:
            if self.main_window and hasattr(self.main_window, 'get_current_svg'):
                return str(self.main_window.get_current_svg())
            return ""
        except Exception as e:
            print(f"获取当前 SVG 失败: {e}")
            return ""
    
    @pyqtSlot(str)
    def show_status_message(self, message):
        """显示状态消息"""
        try:
            if self.main_window and hasattr(self.main_window, 'show_status_message'):
                self.main_window.show_status_message(message)
        except Exception as e:
            print(f"显示状态消息失败: {e}")
