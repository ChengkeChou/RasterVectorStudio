// Paper.js SVG编辑器
// 提供精确的命中测试、元素选择和颜色编辑功能

class PaperJSEditor {
    constructor() {
        this.canvas = document.getElementById('paperCanvas');
        this.currentTool = 'select';
        this.currentColor = '#000000';
        this.selectedItems = [];
        this.toolInfo = document.getElementById('toolInfo');
        this.selectionInfo = document.getElementById('selectionInfo');
        
        this.init();
    }
    
    init() {
        // 设置Paper.js项目
        paper.setup(this.canvas);
        
        // 创建工具
        this.tool = new paper.Tool();
        this.setupEventHandlers();
        
        // 初始化空的SVG内容
        this.loadSvgContent('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"></svg>');
        
        console.log('Paper.js Editor初始化完成');
    }
    
    setupEventHandlers() {
        // 鼠标按下事件
        this.tool.onMouseDown = (event) => {
            this.handleMouseDown(event);
        };
        
        // 鼠标移动事件
        this.tool.onMouseMove = (event) => {
            this.handleMouseMove(event);
        };
        
        // 键盘事件
        this.tool.onKeyDown = (event) => {
            this.handleKeyDown(event);
        };
    }
    
    handleMouseDown(event) {
        switch (this.currentTool) {
            case 'select':
                this.handleSelection(event);
                break;
            case 'picker':
                this.handleColorPicker(event);
                break;
            case 'fill':
                this.handleFillTool(event);
                break;
            default:
                console.log(`工具 ${this.currentTool} 暂未实现`);
        }
    }
    
    handleMouseMove(event) {
        // 实时显示鼠标下的元素信息（可选）
        if (this.currentTool === 'select') {
            const hitResult = paper.project.hitTest(event.point, {
                fill: true,
                stroke: true,
                segments: true,
                tolerance: 5
            });
            
            // 可以在这里显示hover效果
        }
    }
    
    handleKeyDown(event) {
        // Delete键删除选中元素
        if (event.key === 'delete' && this.selectedItems.length > 0) {
            this.deleteSelectedItems();
        }
        
        // Ctrl+A全选
        if (event.key === 'a' && event.modifiers.control) {
            this.selectAll();
            event.preventDefault();
        }
        
        // Escape取消选择
        if (event.key === 'escape') {
            this.clearSelection();
        }
    }
    
    handleSelection(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            segments: true,
            tolerance: 5
        });
        
        if (!event.modifiers.shift) {
            // 如果没有按住Shift，清除之前的选择
            this.clearSelection();
        }
        
        if (hitResult && hitResult.item) {
            const item = hitResult.item;
            
            if (event.modifiers.shift && item.selected) {
                // Shift+点击已选中的项目 = 取消选择
                this.deselectItem(item);
            } else {
                // 选择项目
                this.selectItem(item);
            }
        }
        
        this.updateSelectionInfo();
        paper.view.draw();
    }
    
    handleColorPicker(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            tolerance: 5
        });
        
        if (hitResult && hitResult.item) {
            const item = hitResult.item;
            let pickedColor = null;
            
            // 优先拾取填充色
            if (item.fillColor) {
                pickedColor = item.fillColor.toCSS(true);
            } else if (item.strokeColor) {
                pickedColor = item.strokeColor.toCSS(true);
            }
            
            if (pickedColor) {
                this.currentColor = pickedColor;
                // 通知Python端颜色已更新
                this.notifyColorPicked(pickedColor);
                console.log(`拾取颜色: ${pickedColor}`);
            }
        }
    }
    
    handleFillTool(event) {
        const hitResult = paper.project.hitTest(event.point, {
            fill: true,
            stroke: true,
            tolerance: 5
        });
        
        if (hitResult && hitResult.item) {
            this.applyColorToItem(hitResult.item, this.currentColor);
            paper.view.draw();
        }
    }
    
    selectItem(item) {
        if (!item.selected) {
            item.selected = true;
            this.selectedItems.push(item);
            
            // 添加选择框样式
            this.highlightSelectedItem(item);
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
            if (item.className !== 'Group') { // 避免选择辅助元素
                this.selectItem(item);
            }
        });
        this.updateSelectionInfo();
        paper.view.draw();
    }
    
    deleteSelectedItems() {
        this.selectedItems.forEach(item => {
            item.remove();
        });
        this.selectedItems = [];
        this.updateSelectionInfo();
        paper.view.draw();
    }
    
    highlightSelectedItem(item) {
        // Paper.js的selected属性会自动显示选择框
        // 这里可以添加额外的高亮效果
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
    
    // ===== 工具切换 =====
    setTool(toolName) {
        this.currentTool = toolName;
        this.updateToolInfo();
        
        // 根据工具更新鼠标样式
        switch (toolName) {
            case 'select':
                this.canvas.style.cursor = 'default';
                break;
            case 'picker':
                this.canvas.style.cursor = 'crosshair';
                break;
            case 'fill':
                this.canvas.style.cursor = 'pointer';
                break;
            default:
                this.canvas.style.cursor = 'crosshair';
        }
    }
    
    updateToolInfo() {
        const toolNames = {
            'select': '选择工具',
            'picker': '吸管工具',
            'fill': '填充工具',
            'draw_pen': '画笔工具',
            'draw_shapes': '形状工具',
            'eraser': '橡皮擦'
        };
        
        this.toolInfo.textContent = toolNames[this.currentTool] || this.currentTool;
    }
    
    // ===== 颜色操作 =====
    setCurrentColor(color) {
        this.currentColor = color;
        console.log(`当前颜色设置为: ${color}`);
    }
    
    applyColorToSelected(color, mode = 'fill') {
        if (this.selectedItems.length === 0) {
            console.warn('没有选中的元素');
            return false;
        }
        
        this.selectedItems.forEach(item => {
            this.applyColorToItem(item, color, mode);
        });
        
        paper.view.draw();
        return true;
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
            
            console.log(`应用颜色 ${color} 到元素 (模式: ${mode})`);
        } catch (error) {
            console.error('应用颜色失败:', error);
        }
    }
    
    // ===== SVG内容操作 =====
    loadSvgContent(svgString) {
        try {
            // 清除现有内容
            paper.project.clear();
            
            if (svgString && svgString.trim()) {
                // 导入SVG
                const imported = paper.project.importSVG(svgString);
                if (imported) {
                    // 确保内容适应画布
                    this.fitContentToCanvas();
                    console.log('SVG内容加载成功');
                } else {
                    console.warn('SVG导入失败');
                }
            }
            
            paper.view.draw();
            this.clearSelection();
        } catch (error) {
            console.error('加载SVG内容失败:', error);
        }
    }
    
    getSvgContent() {
        try {
            return paper.project.exportSVG({ asString: true });
        } catch (error) {
            console.error('导出SVG失败:', error);
            return '';
        }
    }
    
    fitContentToCanvas() {
        const bounds = paper.project.activeLayer.bounds;
        if (bounds.width > 0 && bounds.height > 0) {
            const canvasSize = paper.view.size;
            const scale = Math.min(
                canvasSize.width / bounds.width * 0.9,
                canvasSize.height / bounds.height * 0.9
            );
            
            if (scale < 1) {
                paper.project.activeLayer.scale(scale);
            }
            
            // 居中
            const center = canvasSize.divide(2);
            const layerCenter = paper.project.activeLayer.bounds.center;
            paper.project.activeLayer.translate(center.subtract(layerCenter));
        }
    }
    
    // ===== 与Python通信 =====
    notifyColorPicked(color) {
        // 这个方法会被Python端的JavaScript桥接调用覆盖
        console.log('颜色已拾取:', color);
    }
    
    getSelectedElementIds() {
        return this.selectedItems.map((item, index) => {
            // 如果元素有name属性，使用它作为ID
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

// 初始化函数
function initPaperEditor() {
    paperEditor = new PaperJSEditor();
    
    // 暴露给Python的接口
    window.paperEditor = paperEditor;
    
    // 暴露常用方法到全局
    window.loadSvg = (svgString) => paperEditor.loadSvgContent(svgString);
    window.getSvg = () => paperEditor.getSvgContent();
    window.setTool = (toolName) => paperEditor.setTool(toolName);
    window.setCurrentColor = (color) => paperEditor.setCurrentColor(color);
    window.applyColorToSelected = (color, mode) => paperEditor.applyColorToSelected(color, mode);
    window.getSelectedElements = () => paperEditor.getSelectedElementIds();
    window.getSelectedElementsInfo = () => paperEditor.getSelectedElementsInfo();
    window.clearSelection = () => paperEditor.clearSelection();
    window.selectAll = () => paperEditor.selectAll();
    
    console.log('Paper.js编辑器接口已准备就绪');
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPaperEditor);
} else {
    initPaperEditor();
}
