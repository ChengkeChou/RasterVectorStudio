// Professional Paper.js SVG Editor
// 完整的矢量图形编辑器，包含所有专业工具

class ProfessionalPaperEditor {
    constructor() {
        this.canvas = document.getElementById('paperCanvas');
        this.currentTool = 'select';
        this.currentColors = {
            fill: '#3498db',
            stroke: '#2c3e50'
        };
        this.currentProperties = {
            strokeWidth: 2,
            fillOpacity: 1,
            strokeOpacity: 1
        };
        
        this.selectedItems = [];
        this.isDrawing = false;
        this.currentPath = null;
        this.undoStack = [];
        this.redoStack = [];
        
        // UI元素
        this.statusText = document.getElementById('statusText');
        this.selectionInfo = document.getElementById('selectionInfo');
        this.cursorPos = document.getElementById('cursorPos');
        
        this.init();
    }
    
    init() {
        // 设置Paper.js项目
        paper.setup(this.canvas);
        
        // 设置高质量渲染
        paper.settings.handleSize = 8;
        paper.settings.hitTolerance = 6;
        paper.view.resolution = window.devicePixelRatio || 1;
        
        // 创建工具
        this.tool = new paper.Tool();
        this.setupEventHandlers();
        this.setupUI();
        
        // 初始化空的SVG内容
        this.loadSvgContent('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"></svg>');
        
        // 设置网格背景
        this.createGrid();
        
        console.log('Professional Paper.js Editor初始化完成');
        this.updateStatus('专业SVG编辑器已就绪 - 选择工具开始编辑');
    }
    
    createGrid() {
        // 创建网格背景
        const gridGroup = new paper.Group();
        gridGroup.name = 'grid';
        
        const gridSize = 20;
        const canvasSize = paper.view.size;
        
        // 垂直线
        for (let x = 0; x <= canvasSize.width; x += gridSize) {
            const line = new paper.Path.Line(new paper.Point(x, 0), new paper.Point(x, canvasSize.height));
            line.strokeColor = new paper.Color(0, 0, 0, 0.1);
            line.strokeWidth = x % (gridSize * 5) === 0 ? 0.8 : 0.3;
            gridGroup.addChild(line);
        }
        
        // 水平线
        for (let y = 0; y <= canvasSize.height; y += gridSize) {
            const line = new paper.Path.Line(new paper.Point(0, y), new paper.Point(canvasSize.width, y));
            line.strokeColor = new paper.Color(0, 0, 0, 0.1);
            line.strokeWidth = y % (gridSize * 5) === 0 ? 0.8 : 0.3;
            gridGroup.addChild(line);
        }
        
        gridGroup.sendToBack();
        gridGroup.locked = true;
    }
    
    setupEventHandlers() {
        // 鼠标事件
        this.tool.onMouseDown = (event) => this.handleMouseDown(event);
        this.tool.onMouseDrag = (event) => this.handleMouseDrag(event);
        this.tool.onMouseUp = (event) => this.handleMouseUp(event);
        this.tool.onMouseMove = (event) => this.handleMouseMove(event);
        
        // 键盘事件
        this.tool.onKeyDown = (event) => this.handleKeyDown(event);
        this.tool.onKeyUp = (event) => this.handleKeyUp(event);
    }
    
    setupUI() {
        // 工具按钮事件
        const toolButtons = document.querySelectorAll('.tool-button[data-tool]');
        toolButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.setTool(button.dataset.tool);
                this.updateToolButtons(button);
            });
        });
        
        // 颜色控制
        document.getElementById('fillColor').addEventListener('change', (e) => {
            this.currentColors.fill = e.target.value;
            this.applyToSelected();
        });
        
        document.getElementById('strokeColor').addEventListener('change', (e) => {
            this.currentColors.stroke = e.target.value;
            this.applyToSelected();
        });
        
        // 滑块控制
        this.setupSlider('strokeWidth', (value) => {
            this.currentProperties.strokeWidth = value;
            this.applyToSelected();
        });
        
        this.setupSlider('fillOpacity', (value) => {
            this.currentProperties.fillOpacity = value / 100;
            this.applyToSelected();
        });
        
        this.setupSlider('strokeOpacity', (value) => {
            this.currentProperties.strokeOpacity = value / 100;
            this.applyToSelected();
        });
        
        // 缩放控制
        document.getElementById('zoomIn').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoomOut').addEventListener('click', () => this.zoomOut());
        document.getElementById('zoomReset').addEventListener('click', () => this.zoomReset());
    }
    
    setupSlider(id, callback) {
        const slider = document.getElementById(id);
        const valueSpan = document.getElementById(id + 'Value');
        
        slider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            valueSpan.textContent = id.includes('Opacity') ? value : value;
            callback(value);
        });
    }
    
    updateToolButtons(activeButton) {
        document.querySelectorAll('.tool-button[data-tool]').forEach(btn => {
            btn.classList.remove('active');
        });
        activeButton.classList.add('active');
    }
    
    handleMouseDown(event) {
        this.saveState(); // 保存状态用于撤销
        
        switch (this.currentTool) {
            case 'select':
                this.handleSelection(event);
                break;
            case 'rectangle':
                this.startDrawingRectangle(event);
                break;
            case 'circle':
                this.startDrawingCircle(event);
                break;
            case 'path':
                this.startDrawingPath(event);
                break;
            case 'pen':
                this.handlePenTool(event);
                break;
            case 'brush':
                this.startBrush(event);
                break;
            case 'text':
                this.addText(event);
                break;
            case 'eyedropper':
                this.pickColor(event);
                break;
            case 'fill':
                this.fillTool(event);
                break;
            case 'eraser':
                this.eraseTool(event);
                break;
            case 'zoom':
                this.zoomTool(event);
                break;
            case 'hand':
                this.startPan(event);
                break;
        }
        
        paper.view.draw();
    }
    
    handleMouseDrag(event) {
        switch (this.currentTool) {
            case 'rectangle':
                this.updateRectangle(event);
                break;
            case 'circle':
                this.updateCircle(event);
                break;
            case 'path':
                this.updatePath(event);
                break;
            case 'brush':
                this.updateBrush(event);
                break;
            case 'hand':
                this.updatePan(event);
                break;
        }
        
        paper.view.draw();
    }
    
    handleMouseUp(event) {
        switch (this.currentTool) {
            case 'rectangle':
                this.finishRectangle(event);
                break;
            case 'circle':
                this.finishCircle(event);
                break;
            case 'path':
                this.finishPath(event);
                break;
            case 'brush':
                this.finishBrush(event);
                break;
            case 'hand':
                this.finishPan(event);
                break;
        }
        
        this.isDrawing = false;
        this.currentPath = null;
        paper.view.draw();
    }
    
    handleMouseMove(event) {
        // 更新鼠标位置显示
        this.cursorPos.textContent = `鼠标位置: (${Math.round(event.point.x)}, ${Math.round(event.point.y)})`;
        
        // 显示hover效果
        if (this.currentTool === 'select') {
            const hitResult = paper.project.hitTest(event.point, {
                fill: true,
                stroke: true,
                segments: true,
                tolerance: 8
            });
            
            // 更新鼠标指针
            this.canvas.style.cursor = hitResult ? 'pointer' : 'default';
        }
    }
    
    handleKeyDown(event) {
        // 快捷键处理
        switch (event.key) {
            case 'v':
                this.setTool('select');
                break;
            case 'r':
                this.setTool('rectangle');
                break;
            case 'c':
                this.setTool('circle');
                break;
            case 'p':
                this.setTool('path');
                break;
            case 'n':
                this.setTool('pen');
                break;
            case 'b':
                this.setTool('brush');
                break;
            case 't':
                this.setTool('text');
                break;
            case 'i':
                this.setTool('eyedropper');
                break;
            case 'f':
                this.setTool('fill');
                break;
            case 'e':
                this.setTool('eraser');
                break;
            case 'z':
                this.setTool('zoom');
                break;
            case 'h':
                this.setTool('hand');
                break;
            case 'delete':
            case 'backspace':
                this.deleteSelected();
                break;
            case 'escape':
                this.clearSelection();
                break;
            case 'a':
                if (event.modifiers.control) {
                    this.selectAll();
                    event.preventDefault();
                }
                break;
            case 'z':
                if (event.modifiers.control) {
                    this.undo();
                    event.preventDefault();
                }
                break;
            case 'y':
                if (event.modifiers.control) {
                    this.redo();
                    event.preventDefault();
                }
                break;
        }
        
        this.updateToolUI();
    }
    
    handleKeyUp(event) {
        // 键盘释放事件处理
    }
    
    // === 工具实现 ===
    
    handleSelection(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            segments: true,
            tolerance: 8
        });
        
        if (!event.modifiers.shift) {
            this.clearSelection();
        }
        
        if (hitResult && hitResult.item && hitResult.item.name !== 'grid') {
            const item = hitResult.item;
            
            if (event.modifiers.shift && item.selected) {
                this.deselectItem(item);
            } else {
                this.selectItem(item);
            }
        }
        
        this.updateSelectionInfo();
    }
    
    startDrawingRectangle(event) {
        this.currentPath = new paper.Path.Rectangle(event.point, event.point);
        this.applyCurrentStyle(this.currentPath);
        this.isDrawing = true;
    }
    
    updateRectangle(event) {
        if (this.currentPath && this.isDrawing) {
            this.currentPath.remove();
            this.currentPath = new paper.Path.Rectangle(event.downPoint, event.point);
            this.applyCurrentStyle(this.currentPath);
        }
    }
    
    finishRectangle(event) {
        if (this.currentPath) {
            this.currentPath.name = 'rectangle_' + Date.now();
        }
    }
    
    startDrawingCircle(event) {
        this.currentPath = new paper.Path.Circle(event.point, 1);
        this.applyCurrentStyle(this.currentPath);
        this.isDrawing = true;
    }
    
    updateCircle(event) {
        if (this.currentPath && this.isDrawing) {
            const radius = event.point.getDistance(event.downPoint);
            this.currentPath.remove();
            this.currentPath = new paper.Path.Circle(event.downPoint, radius);
            this.applyCurrentStyle(this.currentPath);
        }
    }
    
    finishCircle(event) {
        if (this.currentPath) {
            this.currentPath.name = 'circle_' + Date.now();
        }
    }
    
    startDrawingPath(event) {
        this.currentPath = new paper.Path();
        this.currentPath.add(event.point);
        this.applyCurrentStyle(this.currentPath);
        this.isDrawing = true;
    }
    
    updatePath(event) {
        if (this.currentPath && this.isDrawing) {
            this.currentPath.add(event.point);
        }
    }
    
    finishPath(event) {
        if (this.currentPath) {
            this.currentPath.name = 'path_' + Date.now();
            this.currentPath.smooth();
        }
    }
    
    handlePenTool(event) {
        // 钢笔工具 - 创建贝塞尔曲线
        if (!this.currentPath) {
            this.currentPath = new paper.Path();
            this.applyCurrentStyle(this.currentPath);
            this.currentPath.add(event.point);
        } else {
            this.currentPath.add(event.point);
        }
    }
    
    startBrush(event) {
        this.currentPath = new paper.Path();
        this.currentPath.add(event.point);
        this.applyCurrentStyle(this.currentPath);
        this.currentPath.strokeWidth = this.currentProperties.strokeWidth * 2;
        this.isDrawing = true;
    }
    
    updateBrush(event) {
        if (this.currentPath && this.isDrawing) {
            this.currentPath.add(event.point);
            this.currentPath.smooth();
        }
    }
    
    finishBrush(event) {
        if (this.currentPath) {
            this.currentPath.name = 'brush_' + Date.now();
        }
    }
    
    addText(event) {
        const text = prompt('请输入文字:', '文字');
        if (text) {
            const pointText = new paper.PointText(event.point);
            pointText.content = text;
            pointText.fontSize = 24;
            pointText.fillColor = this.currentColors.fill;
            pointText.name = 'text_' + Date.now();
        }
    }
    
    pickColor(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            tolerance: 5
        });
        
        if (hitResult && hitResult.item) {
            const item = hitResult.item;
            let pickedColor = null;
            
            if (item.fillColor) {
                pickedColor = item.fillColor.toCSS(true);
                this.currentColors.fill = pickedColor;
                document.getElementById('fillColor').value = pickedColor;
            }
            
            if (item.strokeColor) {
                pickedColor = item.strokeColor.toCSS(true);
                this.currentColors.stroke = pickedColor;
                document.getElementById('strokeColor').value = pickedColor;
            }
            
            this.updateStatus(`已拾取颜色: ${pickedColor}`);
            this.notifyColorPicked(pickedColor);
        }
    }
    
    fillTool(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            tolerance: 8
        });
        
        if (hitResult && hitResult.item && hitResult.item.name !== 'grid') {
            this.applyColorToItem(hitResult.item, this.currentColors.fill, 'fill');
            this.updateStatus('已应用填充颜色');
        }
    }
    
    eraseTool(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            tolerance: 8
        });
        
        if (hitResult && hitResult.item && hitResult.item.name !== 'grid') {
            hitResult.item.remove();
            this.updateStatus('已删除元素');
        }
    }
    
    zoomTool(event) {
        if (event.modifiers.option) {
            this.zoomOut();
        } else {
            this.zoomIn();
        }
    }
    
    startPan(event) {
        this.isDrawing = true;
        this.canvas.style.cursor = 'grab';
    }
    
    updatePan(event) {
        if (this.isDrawing) {
            paper.view.translate(event.delta);
        }
    }
    
    finishPan(event) {
        this.canvas.style.cursor = 'default';
    }
    
    // === 样式和属性 ===
    
    applyCurrentStyle(item) {
        if (!item) return;
        
        item.fillColor = new paper.Color(this.currentColors.fill);
        item.strokeColor = new paper.Color(this.currentColors.stroke);
        item.strokeWidth = this.currentProperties.strokeWidth;
        
        if (item.fillColor) {
            item.fillColor.alpha = this.currentProperties.fillOpacity;
        }
        if (item.strokeColor) {
            item.strokeColor.alpha = this.currentProperties.strokeOpacity;
        }
    }
    
    applyToSelected() {
        this.selectedItems.forEach(item => {
            this.applyCurrentStyle(item);
        });
        paper.view.draw();
    }
    
    applyColorToItem(item, color, mode = 'fill') {
        try {
            const paperColor = new paper.Color(color);
            
            switch (mode) {
                case 'fill':
                    item.fillColor = paperColor;
                    break;
                case 'stroke':
                    item.strokeColor = paperColor;
                    break;
                case 'both':
                    item.fillColor = paperColor;
                    item.strokeColor = paperColor;
                    break;
            }
        } catch (error) {
            console.error('应用颜色失败:', error);
        }
    }
    
    // === 选择管理 ===
    
    selectItem(item) {
        if (!item.selected) {
            item.selected = true;
            this.selectedItems.push(item);
        }
    }
    
    deselectItem(item) {
        if (item.selected) {
            item.selected = false;
            const index = this.selectedItems.indexOf(item);
            if (index > -1) {
                this.selectedItems.splice(index, 1);
            }
        }
    }
    
    clearSelection() {
        this.selectedItems.forEach(item => {
            item.selected = false;
        });
        this.selectedItems = [];
        this.updateSelectionInfo();
    }
    
    selectAll() {
        this.clearSelection();
        paper.project.activeLayer.children.forEach(item => {
            if (item.name !== 'grid') {
                this.selectItem(item);
            }
        });
        this.updateSelectionInfo();
        paper.view.draw();
    }
    
    deleteSelected() {
        this.selectedItems.forEach(item => {
            item.remove();
        });
        this.selectedItems = [];
        this.updateSelectionInfo();
        paper.view.draw();
    }
    
    updateSelectionInfo() {
        const count = this.selectedItems.length;
        const info = this.selectionInfo;
        
        if (count === 0) {
            info.textContent = '未选中任何元素';
            info.style.display = 'none';
        } else {
            info.textContent = `已选中 ${count} 个元素`;
            info.style.display = 'block';
        }
    }
    
    // === 缩放控制 ===
    
    zoomIn() {
        paper.view.zoom *= 1.25;
        paper.view.draw();
    }
    
    zoomOut() {
        paper.view.zoom /= 1.25;
        paper.view.draw();
    }
    
    zoomReset() {
        paper.view.zoom = 1;
        paper.view.center = new paper.Point(400, 300);
        paper.view.draw();
    }
    
    // === 撤销/重做 ===
    
    saveState() {
        const state = paper.project.exportJSON();
        this.undoStack.push(state);
        if (this.undoStack.length > 50) {
            this.undoStack.shift();
        }
        this.redoStack = [];
    }
    
    undo() {
        if (this.undoStack.length > 0) {
            const currentState = paper.project.exportJSON();
            this.redoStack.push(currentState);
            
            const previousState = this.undoStack.pop();
            paper.project.importJSON(previousState);
            paper.view.draw();
        }
    }
    
    redo() {
        if (this.redoStack.length > 0) {
            const currentState = paper.project.exportJSON();
            this.undoStack.push(currentState);
            
            const nextState = this.redoStack.pop();
            paper.project.importJSON(nextState);
            paper.view.draw();
        }
    }
    
    // === 工具切换 ===
    
    setTool(toolName) {
        this.currentTool = toolName;
        
        // 完成当前路径
        if (this.currentPath && toolName !== 'pen') {
            this.currentPath = null;
        }
        
        this.updateStatus(`当前工具: ${this.getToolName(toolName)}`);
        this.updateToolUI();
    }
    
    getToolName(tool) {
        const names = {
            'select': '选择工具',
            'rectangle': '矩形工具',
            'circle': '圆形工具',
            'path': '路径工具',
            'pen': '钢笔工具',
            'brush': '画笔工具',
            'text': '文字工具',
            'eyedropper': '吸管工具',
            'fill': '填充工具',
            'eraser': '橡皮擦',
            'zoom': '缩放工具',
            'hand': '平移工具'
        };
        return names[tool] || tool;
    }
    
    updateToolUI() {
        // 更新工具按钮状态
        const button = document.querySelector(`[data-tool="${this.currentTool}"]`);
        if (button) {
            this.updateToolButtons(button);
        }
        
        // 更新鼠标指针
        const cursors = {
            'select': 'default',
            'rectangle': 'crosshair',
            'circle': 'crosshair',
            'path': 'crosshair',
            'pen': 'crosshair',
            'brush': 'crosshair',
            'text': 'text',
            'eyedropper': 'crosshair',
            'fill': 'pointer',
            'eraser': 'pointer',
            'zoom': 'zoom-in',
            'hand': 'grab'
        };
        
        this.canvas.style.cursor = cursors[this.currentTool] || 'default';
    }
    
    // === SVG内容操作 ===
    
    loadSvgContent(svgString) {
        try {
            // 清除现有内容（除了网格）
            paper.project.activeLayer.children.filter(item => item.name !== 'grid').forEach(item => item.remove());
            
            if (svgString && svgString.trim()) {
                // 导入SVG
                const imported = paper.project.importSVG(svgString);
                if (imported) {
                    this.fitContentToCanvas();
                    console.log('SVG内容加载成功');
                } else {
                    console.warn('SVG导入失败');
                }
            }
            
            // 重新创建网格
            this.createGrid();
            
            paper.view.draw();
            this.clearSelection();
        } catch (error) {
            console.error('加载SVG内容失败:', error);
        }
    }
    
    getSvgContent() {
        try {
            // 临时隐藏网格
            const grid = paper.project.activeLayer.children.find(item => item.name === 'grid');
            if (grid) grid.visible = false;
            
            const svg = paper.project.exportSVG({ asString: true });
            
            // 恢复网格
            if (grid) grid.visible = true;
            
            return svg;
        } catch (error) {
            console.error('导出SVG失败:', error);
            return '';
        }
    }
    
    fitContentToCanvas() {
        const items = paper.project.activeLayer.children.filter(item => item.name !== 'grid');
        if (items.length === 0) return;
        
        const group = new paper.Group(items);
        const bounds = group.bounds;
        
        if (bounds.width > 0 && bounds.height > 0) {
            const canvasSize = paper.view.size;
            const scale = Math.min(
                canvasSize.width / bounds.width * 0.8,
                canvasSize.height / bounds.height * 0.8
            );
            
            if (scale < 1) {
                group.scale(scale);
            }
            
            // 居中
            const center = canvasSize.divide(2);
            const groupCenter = group.bounds.center;
            group.translate(center.subtract(groupCenter));
        }
        
        // 取消分组
        group.ungroup();
    }
    
    // === 状态更新 ===
    
    updateStatus(message) {
        this.statusText.textContent = message;
    }
    
    // === 与Python通信 ===
    
    notifyColorPicked(color) {
        // 这个方法会被Python端覆盖
        console.log('颜色已拾取:', color);
    }
    
    getSelectedElementIds() {
        return this.selectedItems.map((item, index) => {
            return item.name || `item_${index}`;
        });
    }
    
    getSelectedElementsInfo() {
        return this.selectedItems.map((item, index) => {
            return {
                id: item.name || `item_${index}`,
                type: item.className.toLowerCase(),
                bounds: item.bounds,
                fillColor: item.fillColor ? item.fillColor.toCSS(true) : null,
                strokeColor: item.strokeColor ? item.strokeColor.toCSS(true) : null
            };
        });
    }
}

// 全局编辑器实例
let paperEditor;

// 全局函数
function selectAll() {
    if (paperEditor) paperEditor.selectAll();
}

function clearSelection() {
    if (paperEditor) paperEditor.clearSelection();
}

function deleteSelected() {
    if (paperEditor) paperEditor.deleteSelected();
}

// 初始化函数
function initPaperEditor() {
    paperEditor = new ProfessionalPaperEditor();
    
    // 暴露给Python的接口
    window.paperEditor = paperEditor;
    
    // 暴露常用方法到全局
    window.loadSvg = (svgString) => paperEditor.loadSvgContent(svgString);
    window.getSvg = () => paperEditor.getSvgContent();
    window.setTool = (toolName) => paperEditor.setTool(toolName);
    window.setCurrentColor = (color) => {
        paperEditor.currentColors.fill = color;
        document.getElementById('fillColor').value = color;
    };
    window.applyColorToSelected = (color, mode) => {
        paperEditor.selectedItems.forEach(item => {
            paperEditor.applyColorToItem(item, color, mode);
        });
        paper.view.draw();
        return paperEditor.selectedItems.length > 0;
    };
    window.getSelectedElements = () => paperEditor.getSelectedElementIds();
    window.getSelectedElementsInfo = () => paperEditor.getSelectedElementsInfo();
    window.clearSelection = () => paperEditor.clearSelection();
    window.selectAll = () => paperEditor.selectAll();
    
    console.log('Professional Paper.js编辑器接口已准备就绪');
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPaperEditor);
} else {
    initPaperEditor();
}
