from pathlib import Path
from typing import Optional
import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QSplitter, QCheckBox, QFrame, QTabWidget, QTextEdit,
    QProgressBar, QButtonGroup, QRadioButton, QToolBar, 
    QAction, QActionGroup, QDockWidget, QStackedWidget,
    QScrollArea, QSlider, QColorDialog
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QCursor, QColor
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QSize,
    pyqtSlot, QTimer, QPoint
)
import json

# 使用简单常量值
RIGHT_DOCK_AREA = 2
LEFT_DOCK_AREA = 1


class ScalableImageLabel(QLabel):
    """可缩放的图片标签组件"""
    
    # 添加颜色选择信号
    colorPicked = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("border: 2px dashed #ccc; background: #f5f5f5;")
        
        # 缩放相关属性
        self._pixmap = None
        self._scale_factor = 1.0
        self._min_scale = 0.1
        self._max_scale = 5.0
        
        # 鼠标拖拽相关
        self._last_pan_point = QPoint()
        self._is_panning = False
        
        # 颜色吸取相关
        self._color_picker_mode = False
        
        # 设置支持鼠标事件
        self.setMouseTracking(True)
        
        # 父窗口引用（用于更新缩放信息）
        self._main_window = None
        
    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self._main_window = main_window
        
    def set_pixmap(self, pixmap):
        """设置要显示的图片"""
        if pixmap and not pixmap.isNull():
            self._pixmap = pixmap
            self._scale_factor = 1.0
            self._update_display()
        else:
            self._pixmap = None
            self.clear()
            self.setText("请先选择位图文件")
    
    def _update_display(self):
        """更新显示的图片"""
        if not self._pixmap:
            return
            
        # 计算缩放后的尺寸
        scaled_size = self._pixmap.size() * self._scale_factor
        
        # 如果图片小于容器，居中显示；如果大于容器，左上角对齐
        if scaled_size.width() <= self.width() and scaled_size.height() <= self.height():
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # 缩放图片
        scaled_pixmap = self._pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        super().setPixmap(scaled_pixmap)
    
    def get_scale_factor(self):
        return self._scale_factor
        
    def zoom_in(self):
        """放大图片"""
        new_scale = min(self._scale_factor * 1.25, self._max_scale)
        if new_scale != self._scale_factor:
            self._scale_factor = new_scale
            self._update_display()
    
    def zoom_out(self):
        """缩小图片"""
        new_scale = max(self._scale_factor / 1.25, self._min_scale)
        if new_scale != self._scale_factor:
            self._scale_factor = new_scale
            self._update_display()
    
    def reset_zoom(self):
        """重置缩放"""
        self._scale_factor = 1.0
        self._update_display()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self._pixmap:
            return
            
        # 计算适应窗口的缩放比例
        widget_size = self.size()
        pixmap_size = self._pixmap.size()
        
        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()
        
        # 选择较小的缩放比例以确保图片完全显示
        self._scale_factor = min(scale_x, scale_y, self._max_scale)
        self._scale_factor = max(self._scale_factor, self._min_scale)
        self._update_display()
    
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 缩放图片"""
        if not self._pixmap:
            return
            
        # 获取滚轮方向
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        
        # 更新主窗口的缩放信息
        if self._main_window and hasattr(self._main_window, '_update_zoom_info'):
            self._main_window._update_zoom_info()
    
    def get_scale_factor(self):
        """获取当前缩放比例"""
        return self._scale_factor
    
    def set_color_picker_mode(self, enabled):
        """设置颜色吸取模式"""
        self._color_picker_mode = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self._color_picker_mode and event.button() == Qt.MouseButton.LeftButton:
            # 颜色吸取模式
            self._pick_color_at_position(event.pos())
        elif event.button() == Qt.MouseButton.LeftButton:
            # 开始拖拽
            self._is_panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._is_panning and self._last_pan_point:
            # 实现图片拖拽（这里简化处理，主要用于颜色吸取）
            pass
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = False
            self._last_pan_point = None
            if not self._color_picker_mode:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def _pick_color_at_position(self, pos):
        """在指定位置吸取颜色"""
        if not self._pixmap:
            return
        
        # 获取当前显示的缩放图片
        current_pixmap = self.pixmap()
        if not current_pixmap:
            return
        
        # 计算实际的像素位置
        label_size = self.size()
        pixmap_size = current_pixmap.size()
        
        # 计算图片在标签中的实际位置
        alignment = self.alignment()
        if alignment == Qt.AlignmentFlag.AlignCenter:
            # 居中显示
            offset_x = (label_size.width() - pixmap_size.width()) // 2
            offset_y = (label_size.height() - pixmap_size.height()) // 2
        else:
            # 左上角对齐
            offset_x = 0
            offset_y = 0
        
        # 转换为图片坐标
        img_x = pos.x() - offset_x
        img_y = pos.y() - offset_y
        
        # 检查是否在图片范围内
        if (0 <= img_x < pixmap_size.width() and 
            0 <= img_y < pixmap_size.height()):
            
            # 转换为原始图片坐标
            original_x = int(img_x / self._scale_factor)
            original_y = int(img_y / self._scale_factor)
            
            # 确保坐标在原始图片范围内
            if (0 <= original_x < self._pixmap.width() and 
                0 <= original_y < self._pixmap.height()):
                
                # 获取像素颜色
                color = self._pixmap.toImage().pixelColor(original_x, original_y)
                
                # 发射颜色选择信号
                self.colorPicked.emit(color)


# 延迟导入，避免在QApplication创建前导入QWidget子类
# from src.gui.editor_widget import SvgEditorWidget
# 工具适配器也延迟导入
# from src.tools.potrace_adapter import PotracePipeline
# from src.tools.trace_adapter import TraceAdapter
# from src.tools.tracegui_adapter import TraceGuiAdapter
# from src.tools.vtracer_adapter import VTracerAdapter


class VectorizeWorker(QThread):
    """矢量化工作线程"""
    finished = pyqtSignal(str)  # 发送生成的SVG内容
    error = pyqtSignal(str)     # 发送错误信息
    progress = pyqtSignal(str)  # 发送进度信息

    def __init__(self, engine, input_path, params):
        super().__init__()
        self.engine = engine
        self.input_path = input_path
        self.params = params
        self._is_cancelled = False

    def cancel(self):
        """取消运行"""
        self._is_cancelled = True

    def run(self):
        temp_files = []  # 用于跟踪临时文件
        try:
            if self._is_cancelled:
                return
                
            self.progress.emit("正在初始化...")
            
            if self._is_cancelled:
                return
            if self.engine == "mkbitmap+potrace":
                # 延迟导入避免Qt问题
                from src.tools.potrace_adapter import PotracePipeline
                pipeline = PotracePipeline()
                
                # 生成唯一的临时文件名
                temp_pbm = Path(self.input_path).with_suffix(f".temp_{os.getpid()}.pbm")
                temp_files.append(temp_pbm)
                
                self.progress.emit("正在运行mkbitmap...")
                svg_text = pipeline.run(
                    self.input_path,
                    threshold=self.params.get('threshold', 128),
                    turdsize=self.params.get('turdsize', 2),
                    alphamax=self.params.get('alphamax', 1.0),
                    edge_mode=self.params.get('edge_mode', False),
                    debug=self.params.get('debug', False),
                    filter_radius=self.params.get('filter_radius', 4),
                    scale_factor=self.params.get('scale_factor', 2),
                    blur_radius=self.params.get('blur_radius', 0.0),
                    turnpolicy=self.params.get('turnpolicy', 'minority'),
                    opttolerance=self.params.get('opttolerance', 0.2),
                    unit=self.params.get('unit', 10),
                    invert=self.params.get('invert', False),
                    longcurve=self.params.get('longcurve', False),
                )
            elif self.engine == "mkbitmap":
                from src.tools.potrace_adapter import PotracePipeline
                pipeline = PotracePipeline()
                
                temp_pbm = Path(self.input_path).with_suffix(f".temp_{os.getpid()}.pbm")
                temp_files.append(temp_pbm)
                
                self.progress.emit("正在运行mkbitmap...")
                pbm_path = pipeline.run_mkbitmap_only(
                    self.input_path,
                    temp_pbm,
                    threshold=self.params.get('threshold', 128),
                    debug=self.params.get('debug', False),
                    filter_radius=self.params.get('filter_radius', 4),
                    scale_factor=self.params.get('scale_factor', 2),
                    blur_radius=self.params.get('blur_radius', 0.0),
                    invert=self.params.get('invert', False),
                )
                svg_text = f"已生成PBM文件: {pbm_path}"
            elif self.engine == "potrace":
                from src.tools.potrace_adapter import PotracePipeline
                pipeline = PotracePipeline()
                self.progress.emit("正在运行potrace...")
                svg_text = pipeline.run_potrace_only(
                    self.input_path,
                    turdsize=self.params.get('turdsize', 2),
                    alphamax=self.params.get('alphamax', 1.0),
                    edge_mode=self.params.get('edge_mode', False),
                    debug=self.params.get('debug', False),
                    turnpolicy=self.params.get('turnpolicy', 'minority'),
                    opttolerance=self.params.get('opttolerance', 0.2),
                    unit=self.params.get('unit', 10),
                    longcurve=self.params.get('longcurve', False),
                )
            elif self.engine == "Trace(.NET)":
                from src.tools.trace_adapter import TraceAdapter
                adapter = TraceAdapter()
                self.progress.emit("正在运行Trace...")
                svg_text = adapter.run(self.input_path)
            elif self.engine == "vtracer":
                try:
                    from src.tools.vtracer_adapter import VTracerAdapter
                    adapter = VTracerAdapter()
                    self.progress.emit("正在运行vtracer...")
                    svg_text = adapter.run(
                        self.input_path,
                        colormode=self.params.get('colormode', 'color'),
                        mode=self.params.get('mode', 'spline'),
                        filter_speckle=self.params.get('filter_speckle', 4),
                        path_precision=self.params.get('path_precision', 8)
                    )
                except Exception as e:
                    raise RuntimeError(f"vtracer不可用: {e}")
            else:
                raise ValueError(f"不支持的引擎: {self.engine}")

            self.progress.emit("完成!")
            self.finished.emit(svg_text)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                        print(f"临时文件已删除: {temp_file}")
                    except Exception as e:
                        print(f"删除临时文件失败 {temp_file}: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RasterVectorStudio - 位图转矢量与本地SVG编辑")
        self._init_state()
        self._init_tools() 
        self._load_styles()
        self._init_ui()
        self._update_all_property_displays()  # 初始化UI显示

    def _init_state(self):
        """初始化状态变量"""
        self.input_path: Optional[Path] = None
        self.output_svg: Optional[Path] = None
        self._pixmap: Optional[QPixmap] = None
        self.worker: Optional[VectorizeWorker] = None
        self.current_mode = "select"  # 当前工具模式
        self.current_panel_mode = "convert"  # 当前面板模式（convert/draw）
        self.editor = None  # 延迟初始化
        
        # 新增：颜色和属性状态
        self.current_fill_color = QColor("#000000")
        self.current_stroke_color = QColor("#555555")
        self.current_stroke_width = 2
        self.has_selection = False  # 新增：用于跟踪是否有选中项

    def _init_tools(self):
        """初始化工具适配器 - 使用局部导入确保QApplication已存在"""
        # ✅ 局部导入：在这个方法内部导入，此时 QApplication 肯定已经存在了！
        # 这样可以避免在模块加载时意外触发Qt组件创建
        
        try:
            from src.tools.potrace_adapter import PotracePipeline
            self.potrace = PotracePipeline()
        except Exception as e:
            print(f"加载 potrace 工具失败: {e}")
            self.potrace = None
            
        try:
            from src.tools.trace_adapter import TraceAdapter
            self.trace = TraceAdapter()
        except Exception as e:
            print(f"加载 trace 工具失败: {e}")
            self.trace = None
            
        try:
            from src.tools.tracegui_adapter import TraceGuiAdapter
            self.tracegui = TraceGuiAdapter()
        except Exception as e:
            print(f"加载 tracegui 工具失败: {e}")
            self.tracegui = None
            
        try:
            from src.tools.vtracer_adapter import VTracerAdapter
            self.vtracer = VTracerAdapter()
        except Exception as e:
            print(f"加载 vtracer 工具失败: {e}")
            self.vtracer = None
        
    # 删除之前的延迟获取方法，因为现在在_init_tools中直接初始化

    def _load_styles(self):
        """加载样式表"""
        try:
            styles_path = Path(__file__).parent / "styles.qss"
            if styles_path.exists():
                with open(styles_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                print(f"样式文件未找到: {styles_path}")
        except Exception as e:
            print(f"加载样式失败: {e}")

    def _init_ui(self):
        """构建用户界面 - 修复版本，解决组件重叠问题"""
        
        # ======================================================================
        # 1. 中央工作区 (预览 + 编辑器)
        # ======================================================================
        central_widget = self._create_central_widget()
        self.setCentralWidget(central_widget)

        # ======================================================================
        # 2. 工具栏 (明确指定位置)
        # ======================================================================
        self._create_toolbars()

        # ======================================================================
        # 3. 停靠面板 (明确指定位置和顺序)
        # ======================================================================
        self._create_dock_widgets()

        # ======================================================================
        # 4. 窗口初始状态和状态栏
        # ======================================================================
        
        # 添加状态栏
        self.lbl_status = QLabel("就绪")
        self.statusBar().addWidget(self.lbl_status)
        
        self.resize(1400, 900)
        self.setMinimumSize(800, 600)
        
        # 安装事件过滤器用于颜色拾取
        self.img_label.installEventFilter(self)

    def _create_central_widget(self):
        """创建中央工作区 - 修复布局"""
        
        # --- 左侧面板 ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # 预览组
        preview_group = QGroupBox("输入预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.img_label = ScalableImageLabel()
        self.img_label.set_main_window(self)
        self.img_label.colorPicked.connect(self._on_color_picked)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.img_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(scroll_area, 1) # stretch = 1
        
        # 缩放控制
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        self.btn_zoom_in = QPushButton("放大 (+)")
        self.btn_zoom_out = QPushButton("缩小 (-)")
        self.btn_zoom_reset = QPushButton("原始大小")
        self.btn_zoom_fit = QPushButton("适应窗口")
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        self.btn_zoom_reset.clicked.connect(self._zoom_reset)
        self.btn_zoom_fit.clicked.connect(self._zoom_fit)
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_layout.addWidget(self.btn_zoom_reset)
        zoom_layout.addWidget(self.btn_zoom_fit)
        preview_layout.addWidget(zoom_widget)
        
        self.zoom_label = QLabel("缩放: 100%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.zoom_label)
        
        left_layout.addWidget(preview_group, stretch=3) # 预览占3份

        # 参数面板 - 使用模式切换面板
        self.param_stack_container = QGroupBox("参数设置")
        param_stack_layout = QVBoxLayout(self.param_stack_container)
        
        # 创建模式切换按钮
        mode_buttons_widget = QWidget()
        mode_buttons_layout = QHBoxLayout(mode_buttons_widget)
        mode_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_convert = QPushButton("🔄 转换工具")
        self.btn_convert.setCheckable(True)
        self.btn_convert.setChecked(True)
        self.btn_convert.clicked.connect(lambda: self._switch_panel_mode("convert"))
        
        self.btn_draw_tools = QPushButton("🎨 绘画工具")
        self.btn_draw_tools.setCheckable(True)
        self.btn_draw_tools.clicked.connect(lambda: self._switch_panel_mode("draw"))
        
        mode_buttons_layout.addWidget(self.btn_convert)
        mode_buttons_layout.addWidget(self.btn_draw_tools)
        param_stack_layout.addWidget(mode_buttons_widget)
        
        # 创建参数面板容器
        param_container = self._create_vectorize_panel()
        param_stack_layout.addWidget(param_container)
        
        left_layout.addWidget(self.param_stack_container, stretch=2) # 参数占2份
        
        # --- 右侧编辑器 ---
        editor_group = QGroupBox("SVG编辑器")
        editor_layout = QVBoxLayout(editor_group)
        editor_layout.setContentsMargins(5, 5, 5, 5)
        
        self.editor_tabs = QTabWidget()
        
        # Web编辑器
        web_tab = QWidget()
        web_layout = QVBoxLayout(web_tab)
        web_layout.setContentsMargins(0, 0, 0, 0)
        try:
            from src.gui.editor_widget import SvgEditorWidget
            self.editor = SvgEditorWidget(main_window=self)
            web_layout.addWidget(self.editor)
        except Exception as e:
            web_layout.addWidget(QLabel(f"编辑器加载失败: {e}"))
            self.editor = None
        self.editor_tabs.addTab(web_tab, "📝 Web编辑器")
        
        # 文本编辑器
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("SVG代码将在这里显示...")
        text_layout.addWidget(self.text_editor)
        self.editor_tabs.addTab(text_tab, "📄 文本编辑器")
        
        editor_layout.addWidget(self.editor_tabs)

        # --- 主分割器 ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(editor_group)
        
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([400, 1000]) # 初始大小

        return main_splitter

    def _update_zoom_info(self):
        """更新缩放信息显示"""
        if hasattr(self, 'zoom_label') and hasattr(self.img_label, 'get_scale_factor'):
            scale_percent = int(self.img_label.get_scale_factor() * 100)
            self.zoom_label.setText(f"缩放: {scale_percent}%")
    
    def _zoom_in(self):
        """放大预览图"""
        if hasattr(self.img_label, 'zoom_in'):
            self.img_label.zoom_in()
            self._update_zoom_info()
            
    def _zoom_out(self):
        """缩小预览图"""
        if hasattr(self.img_label, 'zoom_out'):
            self.img_label.zoom_out()
            self._update_zoom_info()
            
    def _zoom_reset(self):
        """重置预览图缩放"""
        if hasattr(self.img_label, 'reset_zoom'):
            self.img_label.reset_zoom()
            self._update_zoom_info()
            
    def _zoom_fit(self):
        """适应窗口显示预览图"""
        if hasattr(self.img_label, 'fit_to_window'):
            self.img_label.fit_to_window()
            self._update_zoom_info()

    def _create_toolbars(self):
        """创建工具栏，明确指定位置"""
        
        # --- 顶部主工具栏 ---
        top_toolbar = QToolBar("文件操作")
        self.addToolBar(top_toolbar)  # 简化，移除区域指定
        
        # 文件操作按钮
        self.btn_open = QPushButton("📁 打开位图")
        self.btn_open.clicked.connect(self._open_bitmap)
        self.btn_open.setToolTip("选择要转换的位图文件")
        
        self.btn_save = QPushButton("💾 另存SVG")
        self.btn_save.clicked.connect(self._save_svg)
        self.btn_save.setToolTip("保存生成的SVG文件")
        
        top_toolbar.addWidget(self.btn_open)
        top_toolbar.addWidget(self.btn_save)
        top_toolbar.addSeparator()
        
        # --- 左侧垂直工具栏 ---
        left_toolbar = QToolBar("绘图工具")
        left_toolbar.setObjectName("LeftToolBar")
        # 移除方向设置避免Qt常量问题
        self.addToolBar(left_toolbar)  # 简化，移除区域指定
        
        # 创建工具按钮组（互斥选择）
        tool_group = QActionGroup(self)
        tool_group.setExclusive(True)

        # 定义工具
        tools = [
            ("🔍\n选择", "select", "选择和移动SVG元素（在右侧编辑器中选中元素后可使用'仅选中元素'模式）"),
            ("✏️\n画笔", "draw_pen", "自由绘制路径"),
            ("⭕\n形状", "draw_shapes", "绘制几何形状"),
            ("💧\n吸管", "picker", "从预览图像中拾取颜色"),
            ("🪣\n填充", "fill", "填充区域颜色"),
            ("🧽\n擦除", "eraser", "擦除元素")
        ]

        for text, mode, tooltip in tools:
            action = QAction(text, self)
            action.setCheckable(True)
            action.setToolTip(tooltip)
            action.triggered.connect(lambda checked, m=mode: self._set_mode(m))
            
            if mode == "select":
                action.setChecked(True)  # 默认选中选择工具
            
            tool_group.addAction(action)
            left_toolbar.addAction(action)

    def _create_dock_widgets(self):
        """创建侧边参数面板，直接集成到主布局中"""
        # 参数面板已经在左侧布局中创建，这里不需要重复创建
        pass

    def _create_vectorize_panel(self):
        """创建右侧参数面板 - 支持转换和绘画两种模式"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # 创建堆叠面板，用于切换不同的功能模式
        self.mode_stack = QStackedWidget()
        layout.addWidget(self.mode_stack)

        # 创建转换工具面板
        self._create_convert_panel()
        
        # 创建绘画工具面板
        self._create_draw_panel()
        
        # 默认显示转换面板
        self.mode_stack.setCurrentIndex(0)
        self.current_panel_mode = "convert"

        return widget
    
    def _create_convert_panel(self):
        """创建转换工具面板（矢量化相关）"""
        convert_widget = QWidget()
        layout = QVBoxLayout(convert_widget)
        layout.setSpacing(10)

        # 面板标题
        title_label = QLabel("🔄 矢量化转换")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title_label)
        
        layout.addWidget(QFrame())  # 分割线

        # 引擎选择
        layout.addWidget(QLabel("引擎选择:"))
        self.cmb_engine = QComboBox()
        self.cmb_engine.addItems([
            "mkbitmap+potrace", "mkbitmap", "potrace",
            "Trace(.NET)", "vtracer"
        ])
        self.cmb_engine.currentTextChanged.connect(self._on_engine_changed)
        layout.addWidget(self.cmb_engine)

        layout.addWidget(QFrame())  # 分割线

        # 动态参数面板 - 添加滚动区域
        params_scroll = QScrollArea()
        params_scroll.setWidgetResizable(True)
        params_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        params_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建参数容器
        params_container = QWidget()
        self.param_stack = QStackedWidget()
        
        # 将堆叠面板放入容器
        container_layout = QVBoxLayout(params_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.param_stack)
        
        # 设置滚动区域的内容
        params_scroll.setWidget(params_container)
        layout.addWidget(params_scroll)

        # 为不同引擎创建参数面板
        self._create_potrace_params()
        self._create_trace_params()
        self._create_vtracer_params()

        layout.addStretch()

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 开始按钮
        self.btn_run = QPushButton("⚡ 开始矢量化")
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.clicked.connect(self._vectorize)
        layout.addWidget(self.btn_run)
        
        # 添加到堆叠面板
        self.mode_stack.addWidget(convert_widget)
    
    def _create_draw_panel(self):
        """创建绘画工具面板（颜色和绘画相关）"""
        draw_widget = QWidget()
        main_layout = QVBoxLayout(draw_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 面板标题
        title_label = QLabel("🎨 绘画工具")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        main_layout.addWidget(title_label)
        
        main_layout.addWidget(QFrame())  # 分割线

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(10)

        # 绘画工具设置（包含颜色选择）
        self._create_drawing_settings(layout)

        layout.addStretch()
        
        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 添加到堆叠面板
        self.mode_stack.addWidget(draw_widget)
    
    def _create_drawing_settings(self, layout):
        """创建简洁的颜色编辑面板"""
        
        # --- 当前选中元素信息 ---
        selection_group = QGroupBox("选中元素")
        selection_layout = QVBoxLayout(selection_group)
        
        self.lbl_selection_info = QLabel("未选中任何元素")
        self.lbl_selection_info.setWordWrap(True)
        self.lbl_selection_info.setStyleSheet("color: #666; font-style: italic;")
        selection_layout.addWidget(self.lbl_selection_info)
        
        layout.addWidget(selection_group)
        
        # --- 颜色编辑区域 ---
        color_group = QGroupBox("颜色编辑")
        color_layout = QVBoxLayout(color_group)
        
        # 填充颜色
        fill_layout = QHBoxLayout()
        fill_layout.addWidget(QLabel("填充:"))
        self.btn_fill_color = QPushButton()
        self.btn_fill_color.setFixedSize(80, 30)
        self.btn_fill_color.setToolTip("点击选择填充颜色")
        self.btn_fill_color.clicked.connect(self._on_select_fill_color)
        fill_layout.addWidget(self.btn_fill_color)
        fill_layout.addStretch()
        color_layout.addLayout(fill_layout)

        # 描边颜色
        stroke_layout = QHBoxLayout()
        stroke_layout.addWidget(QLabel("描边:"))
        self.btn_stroke_color = QPushButton()
        self.btn_stroke_color.setFixedSize(80, 30)
        self.btn_stroke_color.setToolTip("点击选择描边颜色")
        self.btn_stroke_color.clicked.connect(self._on_select_stroke_color)
        stroke_layout.addWidget(self.btn_stroke_color)
        stroke_layout.addStretch()
        color_layout.addLayout(stroke_layout)

        # 描边宽度
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("宽度:"))
        self.spin_stroke_width = QSpinBox()
        self.spin_stroke_width.setRange(0, 20)
        self.spin_stroke_width.setValue(self.current_stroke_width)
        self.spin_stroke_width.valueChanged.connect(self._on_stroke_width_changed)
        width_layout.addWidget(self.spin_stroke_width)
        width_layout.addStretch()
        color_layout.addLayout(width_layout)
        
        layout.addWidget(color_group)
        
        # --- 操作说明 ---
        help_group = QGroupBox("操作说明")
        help_layout = QVBoxLayout(help_group)
        help_text = QLabel("""
        1. 使用"选择"工具在右侧画布点击元素
        2. 使用"吸管"工具从左侧原图吸取颜色
        3. 选中元素后可修改填充色和描边色
        """)
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 10px;")
        help_layout.addWidget(help_text)
        layout.addWidget(help_group)
    
    def _switch_panel_mode(self, mode):
        """切换面板模式"""
        self.current_panel_mode = mode
        
        if mode == "convert":
            self.mode_stack.setCurrentIndex(0)
            self.btn_convert.setChecked(True)
            self.btn_draw_tools.setChecked(False)
        elif mode == "draw":
            self.mode_stack.setCurrentIndex(1)
            self.btn_convert.setChecked(False)
            self.btn_draw_tools.setChecked(True)
            
        # 更新状态显示
        self.lbl_status.setText(f"当前模式: {'转换工具' if mode == 'convert' else '绘画工具'}")

    def _create_properties_panel(self):
        """创建全新的"颜色与属性"面板UI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- 填充颜色 ---
        fill_group = QGroupBox("填充")
        fill_layout = QHBoxLayout(fill_group)
        self.btn_fill_color = QPushButton()
        self.btn_fill_color.setFixedSize(60, 30)
        self.btn_fill_color.setToolTip("点击选择填充颜色")
        self.btn_fill_color.clicked.connect(self._on_select_fill_color)
        fill_layout.addWidget(self.btn_fill_color, stretch=1)
        layout.addWidget(fill_group)

        # --- 描边颜色 ---
        stroke_group = QGroupBox("描边")
        stroke_layout = QHBoxLayout(stroke_group)
        self.btn_stroke_color = QPushButton()
        self.btn_stroke_color.setFixedSize(60, 30)
        self.btn_stroke_color.setToolTip("点击选择描边颜色")
        self.btn_stroke_color.clicked.connect(self._on_select_stroke_color)
        stroke_layout.addWidget(self.btn_stroke_color, stretch=1)
        layout.addWidget(stroke_group)

        # --- 描边宽度 ---
        stroke_width_group = QGroupBox("描边宽度")
        stroke_width_layout = QHBoxLayout(stroke_width_group)
        self.slider_stroke_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_stroke_width.setRange(1, 100)
        self.slider_stroke_width.setValue(self.current_stroke_width)
        self.spin_stroke_width = QSpinBox()
        self.spin_stroke_width.setRange(1, 100)
        self.spin_stroke_width.setValue(self.current_stroke_width)
        
        # 信号连接
        self.slider_stroke_width.valueChanged.connect(self.spin_stroke_width.setValue)
        self.spin_stroke_width.valueChanged.connect(self.slider_stroke_width.setValue)
        self.slider_stroke_width.valueChanged.connect(self._on_stroke_width_changed)

        stroke_width_layout.addWidget(self.slider_stroke_width)
        stroke_width_layout.addWidget(self.spin_stroke_width)
        layout.addWidget(stroke_width_group)

        layout.addStretch()
        return widget

    def _update_color_button_style(self, button, color):
        """更新颜色按钮的样式"""
        button.setStyleSheet(f"""
            QPushButton {{
                background: {color.name()};
                border: 2px solid #ccc;
                border-radius: 6px;
                color: {'white' if color.lightness() < 128 else 'black'};
                font-weight: bold;
            }}
        """)
        button.setText(color.name())

    def _on_select_fill_color(self):
        """选择填充颜色"""
        color = QColorDialog.getColor(self.current_fill_color, self, "选择填充颜色")
        if color.isValid():
            self.current_fill_color = color
            self._update_color_button_style(self.btn_fill_color, color)
            # 发送指令到JavaScript
            if self.editor:
                self.editor.run_javascript(f"updateProperty('fillColor', '{color.name()}')")

    def _on_select_stroke_color(self):
        """选择描边颜色"""
        color = QColorDialog.getColor(self.current_stroke_color, self, "选择描边颜色")
        if color.isValid():
            self.current_stroke_color = color
            self._update_color_button_style(self.btn_stroke_color, color)
            # 发送指令到JavaScript
            if self.editor:
                self.editor.run_javascript(f"updateProperty('strokeColor', '{color.name()}')")

    def _on_stroke_width_changed(self, value):
        """描边宽度改变"""
        self.current_stroke_width = value
        print(f"描边宽度设置为: {value}")
        # 发送指令到JavaScript
        if self.editor:
            self.editor.run_javascript(f"updateProperty('strokeWidth', {value})")

    def _update_all_property_displays(self):
        """更新所有属性显示"""
        if hasattr(self, 'btn_fill_color'):
            self._update_color_button_style(self.btn_fill_color, self.current_fill_color)
        if hasattr(self, 'btn_stroke_color'):
            self._update_color_button_style(self.btn_stroke_color, self.current_stroke_color)
        if hasattr(self, 'spin_stroke_width'):
            self.spin_stroke_width.setValue(self.current_stroke_width)

    @pyqtSlot(str)
    def on_selection_changed(self, properties_json):
        """
        [核心] 这是一个由JavaScript调用的槽函数。
        当画布上的选中项改变时，JS会调用它来更新PyQt的UI。
        """
        print(f"JS -> PY: 选中项已改变: {properties_json}")
        try:
            # 解析从JS传来的JSON字符串
            props = json.loads(properties_json)
            
            # 如果 props 为空对象，表示没有选中任何东西
            if not props:
                self.has_selection = False
                if hasattr(self, 'lbl_selection_info'):
                    self.lbl_selection_info.setText("未选中任何元素")
                    self.lbl_selection_info.setStyleSheet("color: #666; font-style: italic;")
                return

            self.has_selection = True
            
            # 根据JS传来的属性，更新Python的状态变量
            if 'fillColor' in props and props['fillColor']:
                self.current_fill_color = QColor(props['fillColor'])
            if 'strokeColor' in props and props['strokeColor']:
                self.current_stroke_color = QColor(props['strokeColor'])
            if 'strokeWidth' in props:
                self.current_stroke_width = int(props['strokeWidth'])
            
            # 更新选中元素信息显示
            if hasattr(self, 'lbl_selection_info'):
                info = "已选中元素\n"
                if 'fillColor' in props and props['fillColor']:
                    info += f"填充: {props['fillColor']}\n"
                if 'strokeColor' in props and props['strokeColor']:
                    info += f"描边: {props['strokeColor']}\n"
                if 'strokeWidth' in props:
                    info += f"宽度: {props['strokeWidth']}"
                self.lbl_selection_info.setText(info)
                self.lbl_selection_info.setStyleSheet("color: #333; font-weight: bold;")
            
            # 更新UI以反映新状态
            self._update_all_property_displays()

        except json.JSONDecodeError:
            print("错误：无法解析来自JS的JSON")
        except Exception as e:
            print(f"处理选中项改变时出错: {e}")

    @pyqtSlot(str)
    def on_color_picked(self, hex_color):
        """处理从JavaScript传来的颜色拾取事件"""
        print(f"JS -> PY: 吸管选择颜色: {hex_color}")
        try:
            color = QColor(hex_color)
            if color.isValid():
                self.current_fill_color = color
                self._update_all_property_displays()
                self.lbl_status.setText(f"已选择颜色: {hex_color}")
        except Exception as e:
            print(f"处理颜色拾取时出错: {e}")

    def _create_potrace_params(self):
        """创建 Potrace 系列引擎的参数面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)  # 减少间距
        layout.setContentsMargins(5, 5, 5, 5)  # 减少边距

        # 基础参数 - 使用更紧凑的水平布局
        basic_group = QGroupBox("基础参数")
        basic_layout = QVBoxLayout(basic_group)
        basic_layout.setSpacing(3)
        
        # 阈值 - 水平布局
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("阈值:"))
        self.sp_threshold = QSpinBox()
        self.sp_threshold.setRange(0, 255)
        self.sp_threshold.setValue(128)
        self.sp_threshold.setToolTip("黑白二值化的阈值，较小值保留更多细节")
        threshold_layout.addWidget(self.sp_threshold)
        threshold_layout.addStretch()
        basic_layout.addLayout(threshold_layout)

        # turdsize - 水平布局
        turdsize_layout = QHBoxLayout()
        turdsize_layout.addWidget(QLabel("噪点过滤:"))
        self.sp_turdsize = QSpinBox()
        self.sp_turdsize.setRange(0, 1000)
        self.sp_turdsize.setValue(2)
        self.sp_turdsize.setToolTip("过滤小于此大小的斑点，减少噪点")
        turdsize_layout.addWidget(self.sp_turdsize)
        turdsize_layout.addStretch()
        basic_layout.addLayout(turdsize_layout)

        # alphamax - 水平布局
        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(QLabel("平滑度:"))
        self.sp_alphamax = QDoubleSpinBox()
        self.sp_alphamax.setRange(0.0, 2.0)
        self.sp_alphamax.setSingleStep(0.1)
        self.sp_alphamax.setValue(1.0)
        self.sp_alphamax.setToolTip("控制曲线平滑度，值越大曲线越平滑")
        alpha_layout.addWidget(self.sp_alphamax)
        alpha_layout.addStretch()
        basic_layout.addLayout(alpha_layout)
        
        layout.addWidget(basic_group)

        # 添加分组框 - Mkbitmap 参数（仅对mkbitmap+potrace有效）
        mkbitmap_group = QGroupBox("Mkbitmap 参数")
        mkbitmap_layout = QVBoxLayout(mkbitmap_group)
        mkbitmap_layout.setSpacing(3)
        
        # 高通滤波半径 - 水平布局
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("滤波半径:"))
        self.sp_filter_radius = QSpinBox()
        self.sp_filter_radius.setRange(0, 20)
        self.sp_filter_radius.setValue(4)
        self.sp_filter_radius.setToolTip("高通滤波半径，保留细节同时补偿背景渐变")
        filter_layout.addWidget(self.sp_filter_radius)
        filter_layout.addStretch()
        mkbitmap_layout.addLayout(filter_layout)
        
        # 缩放因子 - 水平布局
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("缩放因子:"))
        self.sp_scale_factor = QSpinBox()
        self.sp_scale_factor.setRange(1, 5)
        self.sp_scale_factor.setValue(2)
        self.sp_scale_factor.setToolTip("图像缩放因子，2倍推荐用于potrace")
        scale_layout.addWidget(self.sp_scale_factor)
        scale_layout.addStretch()
        mkbitmap_layout.addLayout(scale_layout)
        
        # 模糊半径 - 水平布局
        blur_layout = QHBoxLayout()
        blur_layout.addWidget(QLabel("模糊半径:"))
        self.sp_blur_radius = QDoubleSpinBox()
        self.sp_blur_radius.setRange(0.0, 10.0)
        self.sp_blur_radius.setSingleStep(0.1)
        self.sp_blur_radius.setValue(0.0)
        self.sp_blur_radius.setToolTip("模糊半径，0为不模糊，1-2适合降噪")
        blur_layout.addWidget(self.sp_blur_radius)
        blur_layout.addStretch()
        mkbitmap_layout.addLayout(blur_layout)
        
        layout.addWidget(mkbitmap_group)
        
        # 添加分组框 - Potrace 高级参数
        potrace_group = QGroupBox("Potrace 高级参数")
        potrace_layout = QVBoxLayout(potrace_group)
        potrace_layout.setSpacing(3)
        
        # 转向策略 - 水平布局
        turn_layout = QHBoxLayout()
        turn_layout.addWidget(QLabel("转向策略:"))
        self.cmb_turnpolicy = QComboBox()
        self.cmb_turnpolicy.addItems([
            "minority", "majority", "black", "white", "right", "left", "random"
        ])
        self.cmb_turnpolicy.setCurrentText("minority")
        self.cmb_turnpolicy.setToolTip("路径分解时的转向策略")
        turn_layout.addWidget(self.cmb_turnpolicy)
        turn_layout.addStretch()
        potrace_layout.addLayout(turn_layout)
        
        # 优化容差 - 水平布局
        opt_layout = QHBoxLayout()
        opt_layout.addWidget(QLabel("优化容差:"))
        self.sp_opttolerance = QDoubleSpinBox()
        self.sp_opttolerance.setRange(0.0, 1.0)
        self.sp_opttolerance.setSingleStep(0.1)
        self.sp_opttolerance.setValue(0.2)
        self.sp_opttolerance.setToolTip("曲线优化容差，较大值产生更平滑但不太准确的曲线")
        opt_layout.addWidget(self.sp_opttolerance)
        opt_layout.addStretch()
        potrace_layout.addLayout(opt_layout)
        
        # 单位量化 - 水平布局
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("单位量化:"))
        self.sp_unit = QSpinBox()
        self.sp_unit.setRange(1, 100)
        self.sp_unit.setValue(10)
        self.sp_unit.setToolTip("输出坐标的量化单位")
        unit_layout.addWidget(self.sp_unit)
        unit_layout.addStretch()
        potrace_layout.addLayout(unit_layout)
        
        layout.addWidget(potrace_group)

        # 选项 - 使用更紧凑的布局
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(2)
        
        self.chk_edges = QCheckBox("细线边缘模式")
        self.chk_edges.setChecked(True)
        self.chk_edges.setToolTip("适用于线条图和细节丰富的图像")
        options_layout.addWidget(self.chk_edges)

        self.chk_debug = QCheckBox("调试模式")
        self.chk_debug.setChecked(False)
        self.chk_debug.setToolTip("保留中间文件用于调试")
        options_layout.addWidget(self.chk_debug)
        
        self.chk_invert = QCheckBox("反转图像")
        self.chk_invert.setChecked(False)
        self.chk_invert.setToolTip("反转输入图像的黑白")
        options_layout.addWidget(self.chk_invert)
        
        self.chk_longcurve = QCheckBox("禁用曲线优化")
        self.chk_longcurve.setChecked(False)
        self.chk_longcurve.setToolTip("禁用曲线优化，产生更大但更准确的文件")
        options_layout.addWidget(self.chk_longcurve)
        
        layout.addWidget(options_group)

        # 移除默认的stretch，让滚动区域控制
        self.param_stack.addWidget(widget)

    def _create_trace_params(self):
        """创建 Trace(.NET) 的参数面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        info_label = QLabel("Trace(.NET) 引擎使用默认参数进行转换。\n"
                           "这是一个基于 .NET 的高质量矢量化引擎，"
                           "适合处理复杂图像。")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 由于Trace.exe的参数较少，我们添加一些处理选项
        options_group = QGroupBox("处理选项")
        options_layout = QVBoxLayout(options_group)
        
        self.chk_trace_debug = QCheckBox("详细输出")
        self.chk_trace_debug.setChecked(False)
        self.chk_trace_debug.setToolTip("启用详细的处理信息输出")
        options_layout.addWidget(self.chk_trace_debug)
        
        layout.addWidget(options_group)

        layout.addStretch()
        self.param_stack.addWidget(widget)

    def _create_vtracer_params(self):
        """创建 VTracer 的参数面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        info_label = QLabel("VTracer 是基于 Rust 的现代矢量化引擎，\n"
                           "处理速度快，输出质量高。")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 颜色模式
        layout.addWidget(QLabel("颜色模式:"))
        self.cmb_vtracer_colormode = QComboBox()
        self.cmb_vtracer_colormode.addItems(["color", "binary"])
        self.cmb_vtracer_colormode.setCurrentText("color")
        self.cmb_vtracer_colormode.setToolTip("color: 彩色模式, binary: 二值模式")
        layout.addWidget(self.cmb_vtracer_colormode)
        
        # 处理模式
        layout.addWidget(QLabel("处理模式:"))
        self.cmb_vtracer_mode = QComboBox()
        self.cmb_vtracer_mode.addItems(["spline", "polygon", "none"])
        self.cmb_vtracer_mode.setCurrentText("spline")
        self.cmb_vtracer_mode.setToolTip("spline: 样条曲线, polygon: 多边形, none: 无平滑")
        layout.addWidget(self.cmb_vtracer_mode)
        
        # 斑点过滤
        layout.addWidget(QLabel("斑点过滤:"))
        self.sp_vtracer_filter_speckle = QSpinBox()
        self.sp_vtracer_filter_speckle.setRange(0, 100)
        self.sp_vtracer_filter_speckle.setValue(4)
        self.sp_vtracer_filter_speckle.setToolTip("过滤小于此大小的斑点")
        layout.addWidget(self.sp_vtracer_filter_speckle)
        
        # 路径精度
        layout.addWidget(QLabel("路径精度:"))
        self.sp_vtracer_path_precision = QSpinBox()
        self.sp_vtracer_path_precision.setRange(1, 20)
        self.sp_vtracer_path_precision.setValue(8)
        self.sp_vtracer_path_precision.setToolTip("路径坐标的精度位数")
        layout.addWidget(self.sp_vtracer_path_precision)

        layout.addStretch()
        self.param_stack.addWidget(widget)

    def _on_engine_changed(self, engine_name):
        """引擎切换时更新参数面板"""
        if engine_name in ["mkbitmap+potrace", "mkbitmap", "potrace"]:
            self.param_stack.setCurrentIndex(0)  # Potrace 参数
        elif engine_name == "Trace(.NET)":
            self.param_stack.setCurrentIndex(1)  # Trace 参数
        elif engine_name == "vtracer":
            self.param_stack.setCurrentIndex(2)  # VTracer 参数

    def _set_mode(self, mode_name):
        """切换工具模式，并通知前端JS"""
        self.current_mode = mode_name
        self.lbl_status.setText(f"当前工具: {mode_name}")
        print(f"模式切换: {self.current_mode}")
        
        # 通过 run_javascript 调用JS函数，激活前端工具
        if hasattr(self, 'editor') and self.editor:
            self.editor.run_javascript(f"window.activateTool && window.activateTool('{mode_name}')")
        
        # 根据工具类型自动切换面板
        drawing_tools = ["draw_pen", "draw_shapes", "picker", "fill", "eraser"]
        
        if mode_name in drawing_tools:
            # 绘画工具 - 切换到绘画面板
            self._switch_panel_mode("draw")
        elif mode_name == "select":
            # 选择工具 - 保持当前面板模式
            pass
        
        # 根据模式设置光标 (在Python端管理)
        if self.current_mode == 'picker':
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # 设置图片预览的颜色吸取模式
        if hasattr(self.img_label, 'set_color_picker_mode'):
            self.img_label.set_color_picker_mode(mode_name == "picker")
            
        # 同步颜色选择按钮状态
        if hasattr(self, 'btn_pick_color') and mode_name == "picker":
            self.btn_pick_color.setChecked(True)
            self.btn_pick_color.setText("🎨 取消选择")
        elif hasattr(self, 'btn_pick_color') and mode_name != "picker":
            self.btn_pick_color.setChecked(False)
            self.btn_pick_color.setText("🎨 选择颜色")

    def _update_preview(self):
        """更新图像预览，使用可缩放组件"""
        if not self._pixmap or self._pixmap.isNull():
            return
        
        # 使用新的可缩放图片组件
        self.img_label.set_pixmap(self._pixmap)
        
        # 更新缩放信息
        self._update_zoom_info()
    
    def _update_zoom_info(self):
        """更新缩放信息显示"""
        if hasattr(self, 'zoom_label') and hasattr(self.img_label, 'get_scale_factor'):
            scale_percent = int(self.img_label.get_scale_factor() * 100)
            self.zoom_label.setText(f"缩放: {scale_percent}%")
    
    def _zoom_in(self):
        """放大图片"""
        self.img_label.zoom_in()
        self._update_zoom_info()
    
    def _zoom_out(self):
        """缩小图片"""
        self.img_label.zoom_out()
        self._update_zoom_info()
    
    def _zoom_reset(self):
        """重置缩放"""
        self.img_label.reset_zoom()
        self._update_zoom_info()
    
    def _zoom_fit(self):
        """适应窗口"""
        self.img_label.fit_to_window()
        self._update_zoom_info()

    def _open_bitmap(self):
        """打开位图文件"""
        file_filter = "图像文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif *.webp *.ico *.ppm *.pbm *.pgm);;PNG文件 (*.png);;JPEG文件 (*.jpg *.jpeg);;TIFF文件 (*.tiff *.tif);;BMP文件 (*.bmp);;所有文件 (*)"
        path, _ = QFileDialog.getOpenFileName(self, "选择位图文件", "", file_filter)
        
        if not path:
            return
            
        self.input_path = Path(path)
        self._pixmap = QPixmap(str(self.input_path))
        
        if not self._pixmap.isNull():
            self._update_preview()
            self.lbl_status.setText(f"已加载: {self.input_path.name}")
        else:
            QMessageBox.warning(self, "错误", "无法加载选中的图像文件")

    def resizeEvent(self, event):
        """窗口大小改变时延迟更新预览，避免拖拽时频繁更新"""
        super().resizeEvent(event)
        
        if hasattr(self, '_pixmap') and self._pixmap and not self._pixmap.isNull():
            # 停止之前的定时器
            if hasattr(self, '_resize_timer'):
                self._resize_timer.stop()
            else:
                # 创建延迟更新定时器
                self._resize_timer = QTimer()
                self._resize_timer.setSingleShot(True)
                self._resize_timer.timeout.connect(self._update_preview)
            
            # 启动定时器，200ms后更新预览
            self._resize_timer.start(200)

    def _vectorize(self):
        """开始矢量化过程"""
        if not self.input_path:
            QMessageBox.warning(self, "提示", "请先选择位图文件")
            return

        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "提示", "正在处理中，请稍候...")
            return

        engine = self.cmb_engine.currentText()

        # 收集参数
        params = {}
        if engine in ["mkbitmap+potrace", "mkbitmap", "potrace"]:
            params = {
                'threshold': self.sp_threshold.value(),
                'turdsize': self.sp_turdsize.value(),
                'alphamax': self.sp_alphamax.value(),
                'edge_mode': self.chk_edges.isChecked(),
                'debug': self.chk_debug.isChecked(),
                # 新增的Mkbitmap参数
                'filter_radius': self.sp_filter_radius.value(),
                'scale_factor': self.sp_scale_factor.value(),
                'blur_radius': self.sp_blur_radius.value(),
                # 新增的Potrace高级参数
                'turnpolicy': self.cmb_turnpolicy.currentText(),
                'opttolerance': self.sp_opttolerance.value(),
                'unit': self.sp_unit.value(),
                'invert': self.chk_invert.isChecked(),
                'longcurve': self.chk_longcurve.isChecked(),
            }
        elif engine == "vtracer":
            params = {
                'colormode': self.cmb_vtracer_colormode.currentText(),
                'mode': self.cmb_vtracer_mode.currentText(),
                'filter_speckle': self.sp_vtracer_filter_speckle.value(),
                'path_precision': self.sp_vtracer_path_precision.value(),
            }
        elif engine == "Trace(.NET)":
            params = {
                'debug': self.chk_trace_debug.isChecked(),
            }

        # 启动处理
        self._start_vectorize_worker(engine, params)

    def _start_vectorize_worker(self, engine, params):
        """启动矢量化工作线程"""
        # 清理之前的线程
        if self.worker:
            self._cleanup_worker()
            
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.btn_run.setEnabled(False)
        self.lbl_status.setText("正在处理...")

        # 创建并启动工作线程
        self.worker = VectorizeWorker(engine, self.input_path, params)
        self.worker.finished.connect(self._on_vectorize_finished)
        self.worker.error.connect(self._on_vectorize_error)
        self.worker.progress.connect(self._on_vectorize_progress)
        self.worker.start()

    def _on_vectorize_finished(self, result):
        """矢量化完成处理"""
        self._cleanup_worker()

        if result.startswith("已生成PBM文件:"):
            QMessageBox.information(self, "完成", result)
            self.lbl_status.setText("PBM文件生成完成")
        else:
            # SVG结果
            try:
                print(f"矢量化完成，SVG长度: {len(result)}")
                print(f"SVG前100个字符: {result[:100]}")
                
                # 确保编辑器已经初始化
                self._ensure_editor_initialized()
                
                # 添加延迟以确保Web视图完全加载
                def load_svg_delayed():
                    try:
                        if self.editor:
                            print("正在加载SVG到编辑器...")
                            print(f"SVG内容预览: {result[:200]}...")
                            self.editor.load_svg(result)
                            print("SVG加载到编辑器完成")
                            
                            # 额外的延迟确保Paper.js处理完成
                            def verify_load():
                                script = "paper.project.activeLayer.children.length"
                                def check_result(count):
                                    print(f"编辑器中的对象数量: {count}")
                                    if count and int(count) > 0:
                                        print("✓ SVG已成功加载到Paper.js画布")
                                    else:
                                        print("✗ SVG可能未正确加载到画布")
                                
                                if hasattr(self.editor, 'view') and self.editor.view:
                                    self.editor.view.page().runJavaScript(script, check_result)
                            
                            QTimer.singleShot(1000, verify_load)
                        else:
                            print("警告：编辑器为None")
                    except Exception as e:
                        print(f"延迟加载SVG失败: {e}")
                
                # 立即加载到文本编辑器
                self.text_editor.setPlainText(result)
                print("SVG已加载到文本编辑器")
                
                # 延迟200ms加载到Web编辑器，确保其完全初始化
                QTimer.singleShot(200, load_svg_delayed)
                
                # 切换到Web编辑器标签页以显示结果
                if hasattr(self, 'editor_tabs'):
                    self.editor_tabs.setCurrentIndex(0)  # Web编辑器是第一个标签
                    print("已切换到Web编辑器标签页")
                
                self.lbl_status.setText("矢量化完成！")
                print("矢量化处理完成")
                
            except Exception as e:
                print(f"SVG加载失败: {e}")
                QMessageBox.warning(self, "警告", f"SVG加载失败: {e}")
                # 即使Web编辑器失败，文本编辑器应该仍然可用
                self.text_editor.setPlainText(result)
                if hasattr(self, 'editor_tabs'):
                    self.editor_tabs.setCurrentIndex(1)  # 切换到文本编辑器

    def _ensure_editor_initialized(self):
        """确保编辑器已正确初始化"""
        if hasattr(self, 'editor') and self.editor:
            print(f"编辑器对象存在: {type(self.editor)}")
            
            if hasattr(self.editor, 'init_web_view'):
                if not hasattr(self.editor, '_web_view_initialized'):
                    try:
                        print("正在初始化Web视图...")
                        self.editor.init_web_view()
                        self.editor._web_view_initialized = True
                        print("Web视图初始化完成")
                    except Exception as e:
                        print(f"Web视图初始化失败: {e}")
                        self.editor = None
                else:
                    print("Web视图已经初始化过")
            else:
                print("编辑器没有init_web_view方法")
        else:
            print("编辑器对象不存在")

    def _on_vectorize_error(self, error_msg):
        """矢量化错误处理"""
        self._cleanup_worker()
        QMessageBox.critical(self, "矢量化失败", f"处理失败:\n{error_msg}")
        self.lbl_status.setText("处理失败")

    def _on_vectorize_progress(self, message):
        """更新进度信息"""
        self.lbl_status.setText(message)

    def _cleanup_worker(self):
        """清理工作线程"""
        if self.worker:
            # 取消线程运行
            if hasattr(self.worker, 'cancel'):
                self.worker.cancel()
            
            # 断开所有信号连接
            try:
                self.worker.finished.disconnect()
                self.worker.error.disconnect()
                self.worker.progress.disconnect()
            except:
                pass  # 忽略断开连接时的错误
            
            # 如果线程还在运行，等待其结束
            if self.worker.isRunning():
                self.worker.wait(1000)  # 等待1秒
                
                # 如果还没结束，强制终止
                if self.worker.isRunning():
                    self.worker.terminate()
                    self.worker.wait(1000)  # 再等待1秒
            
            # 删除线程对象
            self.worker.deleteLater()
            self.worker = None
            
        self.progress_bar.setVisible(False)
        self.btn_run.setEnabled(True)

    def _save_svg(self):
        """保存SVG文件"""
        svg_content = None
        
        # 尝试从编辑器获取SVG
        if self.editor:
            try:
                svg_content = self.editor.get_svg()
            except:
                pass
        
        # 如果编辑器没有内容，从文本编辑器获取
        if not svg_content:
            svg_content = self.text_editor.toPlainText().strip()
            
        if not svg_content:
            QMessageBox.information(self, "提示", "没有可保存的 SVG 内容")
            return

        # 选择保存位置
        file_filter = "SVG文件 (*.svg);;PDF文件 (*.pdf);;EPS文件 (*.eps);;PNG文件 (*.png);;所有文件 (*)"
        default_name = "output.svg"
        if self.input_path:
            default_name = self.input_path.stem + ".svg"
            
        path, _ = QFileDialog.getSaveFileName(self, "保存文件", default_name, file_filter)
        if not path:
            return

        # 保存文件
        try:
            file_path = Path(path)
            suffix = file_path.suffix.lower()
            
            if suffix == '.svg':
                # 直接保存SVG文件
                file_path.write_text(svg_content, encoding="utf-8")
                QMessageBox.information(self, "完成", f"SVG文件已保存:\n{path}")
            elif suffix in ['.pdf', '.eps', '.png']:
                # 对于其他格式，提示用户需要转换
                QMessageBox.information(self, "提示", 
                    f"暂不支持直接保存为{suffix.upper()}格式。\n"
                    f"建议先保存为SVG格式，然后使用其他工具转换。\n"
                    f"正在保存为SVG格式...")
                
                # 强制保存为SVG
                svg_path = file_path.with_suffix('.svg')
                svg_path.write_text(svg_content, encoding="utf-8")
                QMessageBox.information(self, "完成", f"已保存为SVG文件:\n{svg_path}")
            else:
                # 默认保存为文本文件
                file_path.write_text(svg_content, encoding="utf-8")
                QMessageBox.information(self, "完成", f"文件已保存:\n{path}")
                
            self.lbl_status.setText(f"已保存: {file_path.name}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存文件:\n{e}")

    def cleanup(self):
        """在应用程序退出前调用的清理方法。"""
        print("正在执行清理操作...")
        
        # 清理Web编辑器
        if self.editor and hasattr(self.editor, 'view') and self.editor.view:
            try:
                # 停止加载任何正在进行的操作
                self.editor.view.stop()
                
                # 清理页面缓存和资源
                if hasattr(self.editor.view, 'page') and self.editor.view.page():
                    page = self.editor.view.page()
                    if hasattr(page, 'profile'):
                        profile = page.profile()
                        if hasattr(profile, 'clearHttpCache'):
                            profile.clearHttpCache()
                    
                    # 标记页面删除
                    page.deleteLater()
                
                # 标记视图删除
                self.editor.view.deleteLater()
                print("Web编辑器已清理。")
            except Exception as e:
                print(f"清理Web编辑器时出错: {e}")
        
        # 清理工作线程
        if self.worker:
            try:
                if self.worker.isRunning():
                    self.worker.terminate()
                    if not self.worker.wait(3000):  # 等待3秒
                        print("工作线程无法正常终止")
                
                # 断开信号连接
                try:
                    self.worker.finished.disconnect()
                    self.worker.error.disconnect()
                    self.worker.progress.disconnect()
                except:
                    pass
                
                # 删除线程对象
                self.worker.deleteLater()
                self.worker = None
                print("工作线程已清理。")
            except Exception as e:
                print(f"清理工作线程时出错: {e}")
        
        print("清理操作完成。")

    def showEvent(self, event):
        """重写显示事件 - 在窗口首次显示时初始化Web视图"""
        super().showEvent(event)
        # 简单延迟初始化Web视图
        if hasattr(self, 'editor') and self.editor and hasattr(self.editor, 'init_web_view'):
            if not hasattr(self.editor, '_web_view_initialized'):
                try:
                    self.editor.init_web_view()
                    self.editor._web_view_initialized = True
                    print("Web编辑器初始化完成")
                except Exception as e:
                    print(f"Web编辑器初始化失败: {e}")

    def _on_color_picked(self, color):
        """处理从图片中选择的颜色 - 实现吸管填色完整流程"""
        self.current_color = color
        self._update_color_display()
        self.lbl_status.setText(f"已选择颜色: {color.name()}")
        
        # 传递颜色 (Python -> JS): 在获取到颜色后，立即调用JS函数
        if hasattr(self, 'editor') and self.editor:
            hex_color = self.current_color.name()  # #RRGGBB
            self.editor.run_javascript(f"window.setCurrentColor && window.setCurrentColor('{hex_color}')")
        
        # 吸完色后，自动切换回选择工具或填充工具
        self._set_mode('fill')  # 切换到填充工具，用户可以直接在画布上点击填充
        
        # 启用填充按钮
        if hasattr(self, 'btn_fill_svg'):
            self.btn_fill_svg.setEnabled(True)

    def _select_color(self):
        """打开颜色选择对话框"""
        from PyQt5.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.current_color, self, "选择颜色")
        if color.isValid():
            self.current_color = color
            self._update_color_display()
            
            # 传递颜色到Paper.js编辑器 (按照指南的方式)
            if hasattr(self, 'editor') and self.editor:
                hex_color = self.current_color.name()  # #RRGGBB
                self.editor.run_javascript(f"window.setCurrentColor && window.setCurrentColor('{hex_color}')")
            
            # 更新颜色预览按钮 (如果存在)
            if hasattr(self, 'btn_color_preview'):
                self.btn_color_preview.setText(color.name())
                self.btn_color_preview.setStyleSheet(f"""
                    QPushButton {{
                        background: {color.name()};
                        border: 2px solid #ccc;
                        border-radius: 6px;
                        color: {'white' if color.lightness() < 128 else 'black'};
                        font-weight: bold;
                    }}
                """)
            
            # 启用填充按钮
            if hasattr(self, 'btn_fill_svg'):
                self.btn_fill_svg.setEnabled(True)
            
            self.lbl_status.setText(f"已选择颜色: {color.name()}")

    def _update_color_display(self):
        """更新颜色显示"""
        if hasattr(self, 'color_display') and hasattr(self, 'color_info'):
            color_hex = self.current_color.name()
            self.color_display.setStyleSheet(
                f"border: 2px solid #ccc; background: {color_hex};"
            )
            self.color_info.setText(
                f"RGB({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()})"
            )

    def _toggle_color_picker(self):
        """切换颜色吸取模式"""
        if hasattr(self, 'btn_pick_color'):
            if self.btn_pick_color.isChecked():
                self._set_mode("picker")
                self.btn_pick_color.setText("🎨 取消选择")
            else:
                self._set_mode("select")
                self.btn_pick_color.setText("🎨 选择颜色")

    def _set_preset_color(self, color_hex):
        """设置预设颜色"""
        self.current_color = QColor(color_hex)
        self._update_color_display()
        
        # 传递颜色到Paper.js编辑器
        if hasattr(self, 'editor') and self.editor:
            self.editor.run_javascript(f"window.setCurrentColor && window.setCurrentColor('{color_hex}')")
        
        self.lbl_status.setText(f"已设置颜色: {color_hex}")
        
        # 启用填充按钮
        if hasattr(self, 'btn_fill_svg'):
            self.btn_fill_svg.setEnabled(True)

    def _fill_svg_with_color(self):
        """用选择的颜色填充SVG"""
        if not hasattr(self, 'current_color'):
            QMessageBox.warning(self, "提示", "请先选择颜色")
            return
        
        # 获取填充模式
        fill_mode = "fill"  # 默认
        if hasattr(self, 'fill_mode_group'):
            if self.rb_stroke.isChecked():
                fill_mode = "stroke"
            elif self.rb_both.isChecked():
                fill_mode = "both"
        
        # 获取目标模式
        target_mode = "all"  # 默认为所有元素
        if hasattr(self, 'target_mode_group'):
            if self.rb_selected.isChecked():
                target_mode = "selected"
            elif self.rb_similar.isChecked():
                target_mode = "similar"
            else:
                target_mode = "all"  # rb_all.isChecked() 或其他情况
        
        # 检查编辑器是否就绪
        if not hasattr(self, 'editor') or not self.editor:
            QMessageBox.warning(self, "提示", "SVG编辑器未就绪")
            return
        
        # 如果编辑器还没有准备好，使用同步方式
        if not hasattr(self.editor, '_ready') or not self.editor._ready:
            QMessageBox.warning(self, "提示", "SVG编辑器正在加载中，请稍后再试")
            return
        
        self.lbl_status.setText("正在应用颜色...")
        
        # 使用异步方式获取SVG内容
        def on_svg_received(svg_content):
            nonlocal target_mode  # 允许修改外层变量
            try:
                if not svg_content or svg_content == "''":
                    QMessageBox.warning(self, "提示", "没有可填充的SVG内容")
                    self.lbl_status.setText("就绪")
                    return
                
                # 获取选中的元素（如果有的话）
                selected_elements = self._get_selected_elements()
                
                # 如果选择了"仅选中元素"但没有选中任何元素，改为"所有元素"模式
                if target_mode == "selected" and not selected_elements:
                    print("没有选中的元素，将改为应用到所有元素")
                    target_mode = "all"
                    # 通知用户
                    QMessageBox.information(self, "提示", 
                        "没有选中的SVG元素，将改为对所有元素应用颜色。\n"
                        "请在SVG编辑器中选中元素后再使用'仅选中元素'模式。")
                elif target_mode == "selected" and selected_elements:
                    print(f"将对选中的元素应用颜色: {selected_elements}")
                else:
                    selected_elements = []  # 其他模式不需要选中元素列表
                
                # 使用Paper.js编辑器的精确颜色应用
                if hasattr(self.editor, 'apply_color_to_selected') and self.editor:
                    def on_color_applied(success):
                        if success:
                            self.lbl_status.setText(f"颜色应用成功: {target_mode}")
                            print(f"Paper.js颜色应用成功: {self.current_color.name()}, 模式: {fill_mode}, 目标: {target_mode}")
                        else:
                            # 如果Paper.js应用失败，降级到传统方法
                            self._apply_traditional_color_fill(svg_content, fill_mode, target_mode, selected_elements)
                    
                    if target_mode == "selected":
                        # 直接对选中元素应用颜色
                        self.editor.apply_color_to_selected(self.current_color.name(), fill_mode, on_color_applied)
                    else:
                        # 对于"所有元素"模式，先选择所有元素，然后应用颜色
                        if hasattr(self.editor, 'view') and self.editor.view:
                            self.editor.view.page().runJavaScript("window.selectAll && window.selectAll();")
                            # 稍等一下让选择完成
                            QTimer.singleShot(100, lambda: self.editor.apply_color_to_selected(self.current_color.name(), fill_mode, on_color_applied))
                        else:
                            on_color_applied(False)
                else:
                    # 降级到传统方法
                    self._apply_traditional_color_fill(svg_content, fill_mode, target_mode, selected_elements)
                
                # 异步设置回编辑器
                def on_svg_set(success):
                    mode_text = {
                        "fill": "内部填充",
                        "stroke": "线条颜色", 
                        "both": "填充+线条"
                    }[fill_mode]
                    
                    target_text = {
                        "selected": "选中元素",
                        "all": "所有元素",
                        "similar": "相似元素"
                    }[target_mode]
                    
                    if success:
                        self.lbl_status.setText(f"已对{target_text}应用{mode_text}: {self.current_color.name()}")
                        print(f"颜色填充成功: {mode_text} -> {target_text}")
                    else:
                        self.lbl_status.setText("设置SVG内容失败")
                
                if self.editor and hasattr(self.editor, 'set_svg_async'):
                    self.editor.set_svg_async(filled_svg, on_svg_set)
                elif self.editor and hasattr(self.editor, 'set_svg_content'):
                    # 降级到同步方式
                    self.editor.set_svg_content(filled_svg)
                    on_svg_set(True)
                else:
                    self.lbl_status.setText("编辑器方法不可用")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"填充SVG时出错: {str(e)}")
                self.lbl_status.setText("就绪")
                print(f"颜色填充错误: {e}")
        
        # 异步获取SVG内容
        if self.editor and hasattr(self.editor, 'get_svg_async'):
            self.editor.get_svg_async(on_svg_received)
        else:
            # 降级到同步方式
            try:
                svg_content = self.editor.get_svg_content() if self.editor else ""
                on_svg_received(svg_content)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"获取SVG内容失败: {str(e)}")
                self.lbl_status.setText("就绪")

    def _get_selected_elements(self):
        """获取当前选中的SVG元素ID列表"""
        # 使用Paper.js编辑器获取选中元素
        try:
            if hasattr(self, 'editor') and self.editor and hasattr(self.editor, 'get_selected_elements'):
                # 使用Paper.js的精确选择API
                result = []
                def callback(elements):
                    result.extend(elements or [])
                
                self.editor.get_selected_elements(callback)
                
                # 简单等待回调（实际应该使用更好的异步机制）
                import time
                timeout = 0
                while not result and timeout < 5:  # 0.5秒超时
                    time.sleep(0.1)
                    timeout += 1
                
                return result
            return []
        except Exception as e:
            print(f"获取选中元素失败: {e}")
            return []
    
    def _smart_select_first_element(self, svg_content):
        """智能选择第一个可用的SVG元素"""
        import re
        
        # 优先查找path元素，因为它们通常是矢量化的主要内容
        svg_elements = ['path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line']
        
        for element_type in svg_elements:
            pattern = f'<{element_type}[^>]*/?>'
            matches = re.findall(pattern, svg_content)
            if matches:
                # 为第一个找到的元素创建一个临时ID
                first_element = matches[0]
                
                # 检查是否已经有ID
                id_match = re.search(r'id="([^"]*)"', first_element)
                if id_match:
                    element_id = id_match.group(1)
                    print(f"找到已有ID的{element_type}元素: {element_id}")
                    return [element_id]
                else:
                    # 创建临时ID并标记第一个元素
                    temp_id = f"temp_selected_{element_type}_1"
                    print(f"为第一个{element_type}元素创建临时ID: {temp_id}")
                    return [temp_id]
        
        print("没有找到任何SVG图形元素")
        return []

    def _apply_traditional_color_fill(self, svg_content, fill_mode, target_mode, selected_elements):
        """传统的SVG颜色填充方法（作为Paper.js的降级方案）"""
        try:
            # 应用颜色填充
            filled_svg = self._apply_color_fill(
                svg_content, 
                self.current_color.name(),
                fill_mode,
                target_mode,
                selected_elements
            )
            
            print(f"原始SVG长度: {len(svg_content)}")
            print(f"处理后SVG长度: {len(filled_svg)}")
            print(f"填充模式: {fill_mode}, 目标模式: {target_mode}")
            print(f"颜色: {self.current_color.name()}")
            
            # 如果没有变化，提示用户
            if filled_svg == svg_content:
                self.lbl_status.setText("没有找到可填充的SVG元素（可能不包含path、rect等图形元素）")
                print("SVG内容没有变化 - 可能没有找到匹配的元素")
                return
                
            # 将修改后的SVG设置回编辑器
            def on_svg_set(success):
                mode_text = {
                    "fill": "填充颜色", 
                    "stroke": "线条颜色", 
                    "both": "填充+线条"
                }[fill_mode]
                
                target_text = {
                    "selected": "选中元素",
                    "all": "所有元素",
                    "similar": "相似元素"
                }[target_mode]
                
                if success:
                    self.lbl_status.setText(f"已对{target_text}应用{mode_text}: {self.current_color.name()}")
                    print(f"颜色填充成功: {mode_text} -> {target_text}")
                else:
                    self.lbl_status.setText("设置SVG内容失败")
            
            if self.editor and hasattr(self.editor, 'set_svg_async'):
                self.editor.set_svg_async(filled_svg, on_svg_set)
            elif self.editor and hasattr(self.editor, 'set_svg_content'):
                # 降级到同步方式
                self.editor.set_svg_content(filled_svg)
                on_svg_set(True)
            else:
                self.lbl_status.setText("编辑器方法不可用")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"填充SVG时出错: {str(e)}")
            self.lbl_status.setText("就绪")
            print(f"颜色填充错误: {e}")

    def _apply_color_fill(self, svg_content, color_hex, fill_mode="fill", target_mode="all", selected_elements=None):
        """将颜色应用到SVG内容"""
        import re
        
        if selected_elements is None:
            selected_elements = []
        
        print(f"开始颜色填充: 模式={fill_mode}, 目标={target_mode}, 颜色={color_hex}")
        
        # 先修复SVG的width/height NaN问题
        svg_content = self._fix_svg_dimensions(svg_content)
        
        # 根据目标模式决定要处理的元素
        if target_mode == "selected" and not selected_elements:
            print("选中元素模式但没有选中元素，返回原内容")
            return svg_content  # 不做修改
        
        processed_count = 0  # 处理的元素计数
        
        def apply_color_to_element(element_tag, element_type):
            """为单个元素应用颜色"""
            nonlocal processed_count
            modified_tag = element_tag
            original_tag = element_tag
            
            if fill_mode == "fill" or fill_mode == "both":
                # 处理填充颜色
                if 'fill=' in modified_tag:
                    # 替换现有的fill属性
                    modified_tag = re.sub(r'fill="[^"]*"', f'fill="{color_hex}"', modified_tag)
                    modified_tag = re.sub(r"fill='[^']*'", f"fill='{color_hex}'", modified_tag)
                else:
                    # 添加fill属性
                    if modified_tag.endswith('/>'):
                        modified_tag = modified_tag[:-2] + f' fill="{color_hex}"/>'
                    elif modified_tag.endswith('>'):
                        modified_tag = modified_tag[:-1] + f' fill="{color_hex}">'
            
            if fill_mode == "stroke" or fill_mode == "both":
                # 处理线条颜色
                if 'stroke=' in modified_tag:
                    # 替换现有的stroke属性
                    modified_tag = re.sub(r'stroke="[^"]*"', f'stroke="{color_hex}"', modified_tag)
                    modified_tag = re.sub(r"stroke='[^']*'", f"stroke='{color_hex}'", modified_tag)
                else:
                    # 添加stroke属性
                    if modified_tag.endswith('/>'):
                        modified_tag = modified_tag[:-2] + f' stroke="{color_hex}"/>'
                    elif modified_tag.endswith('>'):
                        modified_tag = modified_tag[:-1] + f' stroke="{color_hex}">'
                
                # 确保stroke有合适的宽度
                if 'stroke-width=' not in modified_tag:
                    if modified_tag.endswith('/>'):
                        modified_tag = modified_tag[:-2] + ' stroke-width="1"/>'
                    elif modified_tag.endswith('>'):
                        modified_tag = modified_tag[:-1] + ' stroke-width="1">'
            
            if modified_tag != original_tag:
                processed_count += 1
                print(f"处理了 {element_type} 元素 #{processed_count}")
            
            return modified_tag
        
        def should_process_element(element_tag):
            """判断是否应该处理这个元素"""
            if target_mode == "all":
                return True
            elif target_mode == "selected":
                # 检查元素是否有id属性且在选中列表中
                id_match = re.search(r'id="([^"]*)"', element_tag)
                if id_match:
                    element_id = id_match.group(1)
                    return element_id in selected_elements
                else:
                    # 对于没有ID的元素，检查是否是第一个临时选中的元素
                    for sel_id in selected_elements:
                        if sel_id.startswith("temp_selected_"):
                            # 提取元素类型
                            parts = sel_id.split("_")
                            if len(parts) >= 3:
                                element_type = parts[2]
                                
                                # 检查当前元素是否匹配，并且是第一个
                                if element_tag.startswith(f'<{element_type}'):
                                    # 使用函数属性来跟踪已处理的元素
                                    if not hasattr(should_process_element, 'processed_count'):
                                        should_process_element.processed_count = {}
                                    
                                    key = element_type
                                    if key not in should_process_element.processed_count:
                                        should_process_element.processed_count[key] = 0
                                    
                                    should_process_element.processed_count[key] += 1
                                    # 只处理第一个元素
                                    return should_process_element.processed_count[key] == 1
                return False
            elif target_mode == "similar":
                # 这里可以实现根据元素类型的相似性逻辑
                # 暂时按所有元素处理
                return True
            return False
        
        # 处理不同类型的SVG元素
        svg_elements = ['path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line']
        
        for element_type in svg_elements:
            # 使用正则表达式找到所有该类型的元素
            pattern = f'<{element_type}[^>]*/?>'
            matches = re.findall(pattern, svg_content)
            print(f"找到 {len(matches)} 个 {element_type} 元素")
            
            def replace_element(match):
                element_tag = match.group(0)
                if should_process_element(element_tag):
                    return apply_color_to_element(element_tag, element_type)
                return element_tag
            
            svg_content = re.sub(pattern, replace_element, svg_content)
        
        print(f"总共处理了 {processed_count} 个元素")
        return svg_content
    
    def _fix_svg_dimensions(self, svg_content):
        """修复SVG的width和height属性中的NaN值"""
        import re
        
        def fix_dimension(match):
            attr_name = match.group(1)  # width 或 height
            attr_value = match.group(2)  # 属性值
            
            if attr_value == "NaN" or attr_value == "":
                # 如果是NaN或空值，设置为默认值
                return f'{attr_name}="400"'
            
            # 尝试解析数值
            try:
                # 提取数字部分
                num_match = re.search(r'(\d+(?:\.\d+)?)', attr_value)
                if num_match:
                    return f'{attr_name}="{num_match.group(1)}"'
                else:
                    return f'{attr_name}="400"'
            except:
                return f'{attr_name}="400"'
        
        # 修复width属性
        svg_content = re.sub(r'(width)="([^"]*)"', fix_dimension, svg_content)
        # 修复height属性
        svg_content = re.sub(r'(height)="([^"]*)"', fix_dimension, svg_content)
        
        return svg_content

    def closeEvent(self, event):
        """重写窗口关闭事件 - 只关闭窗口，清理交给 aboutToQuit 信号处理"""
        print("窗口正在关闭...")
        # 不在这里调用 cleanup()，避免与 aboutToQuit 信号重复
        super().closeEvent(event)

    def eventFilter(self, source, event):
        """事件过滤器 - 处理左侧图片的颜色拾取"""
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QMouseEvent
        
        if source is self.img_label and self.current_mode == 'picker' and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                try:
                    # 获取点击位置
                    click_pos = event.pos()
                    
                    # 获取缩放后的图片在控件中的实际位置和大小
                    label_size = self.img_label.size()
                    pixmap = self.img_label.pixmap()
                    
                    if pixmap and not pixmap.isNull():
                        # 计算图片在控件中的显示区域
                        pixmap_size = pixmap.size()
                        
                        # 计算图片的显示位置（居中对齐）
                        x_offset = (label_size.width() - pixmap_size.width()) // 2
                        y_offset = (label_size.height() - pixmap_size.height()) // 2
                        
                        # 检查点击是否在图片区域内
                        if (x_offset <= click_pos.x() <= x_offset + pixmap_size.width() and
                            y_offset <= click_pos.y() <= y_offset + pixmap_size.height()):
                            
                            # 转换为图片坐标
                            img_x = click_pos.x() - x_offset
                            img_y = click_pos.y() - y_offset
                            
                            # 获取原始图片的缩放比例
                            scale_factor = self.img_label.get_scale_factor()
                            original_x = int(img_x / scale_factor)
                            original_y = int(img_y / scale_factor)
                            
                            # 从原始图片获取颜色
                            if hasattr(self, '_pixmap') and self._pixmap:
                                image = self._pixmap.toImage()
                                if (0 <= original_x < image.width() and 0 <= original_y < image.height()):
                                    picked_color = image.pixelColor(original_x, original_y)
                                    
                                    print(f"从原图拾取颜色: {picked_color.name()} at ({original_x}, {original_y})")
                                    
                                    # 更新填充颜色并应用到选中项
                                    self.current_fill_color = picked_color
                                    self._update_all_property_displays()
                                    
                                    # 发送指令到JavaScript
                                    if self.editor:
                                        self.editor.run_javascript(f"updateProperty('fillColor', '{picked_color.name()}')")
                                    
                                    # 切换回选择工具
                                    self._set_mode("select")
                                    
                                    return True
                                    
                except Exception as e:
                    print(f"颜色拾取失败: {e}")
                    
        return super().eventFilter(source, event)
