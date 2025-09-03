// 确保在文档加载完毕后执行
document.addEventListener('DOMContentLoaded', function () {
    console.log("DOMContentLoaded event fired");
    
    // 1. 初始化Paper.js并绑定到canvas
    var canvas = document.getElementById('mainCanvas');
    if (!canvas) {
        console.error("Canvas element with id 'mainCanvas' not found!");
        return;
    }
    
    console.log("Canvas element found:", canvas);
    console.log("Canvas dimensions:", canvas.clientWidth, "x", canvas.clientHeight);
    
    // 配置Paper.js以避免属性错误
    try {
        paper.setup(canvas);
        console.log("Paper.js setup complete");
        console.log("Paper.js view size:", paper.view.size.toString());
        console.log("Paper.js view center:", paper.view.center.toString());
        
        // 强制刷新视图
        paper.view.draw();
        console.log("Paper.js initial draw complete");
    } catch (error) {
        console.error("Paper.js setup error:", error);
        return;
    }

    // =============================================
    // == 全局状态管理
    // =============================================
    
    // 全局状态变量
    var AppState = {
        currentColor: new paper.Color('#000000'), // 默认颜色为黑色
        currentStrokeWidth: 2, // 默认描边宽度
        currentTool: null
    };

    // =============================================
    // == Python 可调用的函数
    // =============================================

    // 2. 增强版的SVG加载函数 (由Python调用)
    window.loadSvg = function(svgString) {
        console.log("Received SVG data, starting import...");

        // 清理旧内容
        paper.project.clear();

        // 导入SVG，这是异步操作
        paper.project.importSVG(svgString, {
            onLoad: function(item) {
                console.log("SVG import successful!");

                // 'item' 是包含所有SVG元素的Group
                if (item && item.bounds) {
                    console.log("SVG bounds:", item.bounds.toString());
                    console.log("View bounds:", paper.view.bounds.toString());
                    
                    // 计算缩放比例以适应视图
                    var viewBounds = paper.view.bounds;
                    var itemBounds = item.bounds;
                    
                    // 计算缩放比例，留出一些边距
                    var scaleX = (viewBounds.width - 100) / itemBounds.width;
                    var scaleY = (viewBounds.height - 100) / itemBounds.height;
                    var scale = Math.min(scaleX, scaleY, 1); // 不放大，只缩小
                    
                    console.log("Calculated scale:", scale);
                    
                    // 应用缩放
                    if (scale < 1) {
                        item.scale(scale);
                        console.log("Applied scale:", scale);
                    }
                    
                    // 居中显示
                    item.position = paper.view.center;
                    console.log("Centered at:", paper.view.center.toString());
                    
                    // 强制刷新视图
                    paper.view.update();
                    
                    console.log("Final item bounds:", item.bounds.toString());
                } else {
                    console.log("Item or bounds not available");
                }

                console.log("SVG content has been centered and fitted to the view.");
                console.log("Total items in project:", paper.project.activeLayer.children.length);
            },
            onError: function(message) {
                console.error("SVG import failed:", message);
            }
        });
    };

    // 获取当前SVG内容
    window.getSvg = function() {
        try {
            return paper.project.exportSVG({ asString: true });
        } catch (error) {
            console.error('导出SVG失败:', error);
            return '';
        }
    };

    // Python 调用此函数来激活不同的工具
    window.activateTool = function(toolName) {
        console.log('激活工具:', toolName);
        AppState.currentMode = toolName;
        
        if (tools[toolName]) {
            tools[toolName].activate();
            console.log(`已激活工具: ${toolName}`);
        } else {
            console.warn(`未知工具: ${toolName}`);
            // 如果是未知工具，默认激活选择工具
            if (tools.select) {
                tools.select.activate();
                AppState.currentMode = 'select';
            }
        }
    };

    // Python 调用此函数来设置当前颜色
    window.setCurrentColor = function(hexColor) {
        console.log('设置颜色:', hexColor);
        AppState.currentColor = new paper.Color(hexColor);
    };

    // 设置描边宽度
    window.setStrokeWidth = function(width) {
        console.log('设置描边宽度:', width);
        AppState.currentStrokeWidth = width;
    };

    // =============================================
    // == Paper.js 工具定义
    // =============================================

    // 创建一个包含所有工具逻辑的对象
    var tools = {
        // --- 选择/移动工具 ---
        select: new paper.Tool(),

        // --- 填充工具 ---
        fill: new paper.Tool(),
        
        // --- 吸管工具 (仅作为状态存在，实际操作在Python中) ---
        picker: new paper.Tool(),

        // --- 画笔工具 ---
        draw_pen: new paper.Tool(),

        // --- 形状工具 ---
        draw_shapes: new paper.Tool(),

        // --- 橡皮擦工具 ---
        eraser: new paper.Tool()
    };

    // --- 为每个工具定义行为 ---

    // 选择工具的鼠标点击事件
    tools.select.onMouseDown = function(event) {
        // 先取消所有项目的选择
        paper.project.deselectAll();
        
        var hitResult = paper.project.hitTest(event.point, { 
            fill: true, 
            stroke: true, 
            segments: true, 
            tolerance: 5 
        });
        if (hitResult) {
            // 选中被点击的项目
            hitResult.item.selected = true;
            console.log('选中元素:', hitResult.item.className);
            
            // 通知Python选中状态改变
            notifyPythonOfSelectionChange();
        } else {
            // 点击空白处，取消选择
            console.log('取消选择');
            notifyPythonOfSelectionChange();
        }
    };

    // 填充工具的鼠标点击事件
    tools.fill.onMouseDown = function(event) {
        var hitResult = paper.project.hitTest(event.point, { fill: true, stroke: true });
        if (hitResult) {
            // 如果点中了图形，就用当前颜色填充它
            hitResult.item.fillColor = AppState.currentColor;
            console.log('填充颜色:', AppState.currentColor.toCSS());
        }
    };

    // 画笔工具
    var currentPath;
    tools.draw_pen.onMouseDown = function(event) {
        // 创建一条新路径，并使用全局状态中的参数
        currentPath = new paper.Path({
            segments: [event.point],
            strokeColor: AppState.currentColor,
            strokeWidth: AppState.currentStrokeWidth,
            strokeCap: 'round'
        });
    };

    tools.draw_pen.onMouseDrag = function(event) {
        if (currentPath) {
            currentPath.add(event.point);
        }
    };

    tools.draw_pen.onMouseUp = function(event) {
        if (currentPath) {
            currentPath.simplify(10); // 平滑路径
            currentPath = null;
        }
    };

    // 形状工具 (矩形示例)
    var startPoint;
    var currentShape;
    tools.draw_shapes.onMouseDown = function(event) {
        startPoint = event.point;
    };

    tools.draw_shapes.onMouseDrag = function(event) {
        if (currentShape) {
            currentShape.remove();
        }
        var rectangle = new paper.Rectangle(startPoint, event.point);
        currentShape = new paper.Path.Rectangle(rectangle);
        currentShape.strokeColor = AppState.currentColor;
        currentShape.strokeWidth = AppState.currentStrokeWidth;
        currentShape.fillColor = null; // 只有边框
    };

    tools.draw_shapes.onMouseUp = function(event) {
        currentShape = null;
    };

    // 橡皮擦工具
    tools.eraser.onMouseDown = function(event) {
        var hitResult = paper.project.hitTest(event.point, { fill: true, stroke: true });
        if (hitResult) {
            hitResult.item.remove();
            console.log('删除元素');
        }
    };

    // 吸管工具 (picker)
    tools.picker = new paper.Tool();
    tools.picker.onMouseDown = function(event) {
        var hitResult = paper.project.hitTest(event.point, { fill: true, stroke: true });
        if (hitResult && hitResult.item) {
            var color = null;
            // 优先获取填充颜色，如果没有则获取描边颜色
            if (hitResult.item.fillColor) {
                color = hitResult.item.fillColor;
            } else if (hitResult.item.strokeColor) {
                color = hitResult.item.strokeColor;
            }
            
            if (color) {
                var hexColor = color.toCSS(true);
                console.log('吸管获取颜色:', hexColor);
                
                // 更新全局状态
                AppState.currentColor = color;
                
                // 通知Python颜色改变
                if (window.pythonBridge && window.pythonBridge.on_color_picked) {
                    window.pythonBridge.on_color_picked(hexColor);
                }
            }
        }
    };

    // 将工具集挂载到全局状态，以便 activateTool 函数可以访问
    AppState.currentTool = tools;

    // 默认激活选择工具
    window.activateTool('select');

    // =============================================
    // == 3. 实现平移和缩放工具
    // =============================================
    
    var panTool = new paper.Tool();
    // 注意：不要激活panTool，让其他工具处理主要交互

    var isPanning = false;

    // =============================================
    // == Python 通信函数
    // =============================================
    
    // 通知Python选中项改变
    function notifyPythonOfSelectionChange() {
        var properties = {};
        var selectedItems = paper.project.selectedItems;
        
        if (selectedItems.length > 0) {
            // 只获取第一个选中项的属性来更新UI
            var firstItem = selectedItems[0];
            
            if (firstItem.fillColor) {
                properties.fillColor = firstItem.fillColor.toCSS(true);
            }
            if (firstItem.strokeColor) {
                properties.strokeColor = firstItem.strokeColor.toCSS(true);
            }
            if (firstItem.strokeWidth !== undefined) {
                properties.strokeWidth = firstItem.strokeWidth;
            }
            if (firstItem.opacity !== undefined) {
                properties.opacity = firstItem.opacity;
            }
        }
        
        // 将JS对象转换为JSON字符串并发送给Python
        var jsonString = JSON.stringify(properties);
        console.log('通知Python选中项改变:', jsonString);
        
        // 通过QWebChannel发送给Python
        if (window.pythonBridge && window.pythonBridge.on_selection_changed) {
            window.pythonBridge.on_selection_changed(jsonString);
        } else {
            console.warn("Python bridge 'backend' not found.");
        }
    }

    // 处理来自Python的属性更新指令
    window.updateProperty = function(key, value) {
        console.log('收到属性更新指令:', key, '=', value);
        
        var selectedItems = paper.project.selectedItems;
        
        if (selectedItems.length > 0) {
            // 只对选中的元素应用属性更改
            selectedItems.forEach(function(item) {
                if (key === 'fillColor') {
                    item.fillColor = new paper.Color(value);
                } else if (key === 'strokeColor') {
                    item.strokeColor = new paper.Color(value);
                } else if (key === 'strokeWidth') {
                    item.strokeWidth = parseFloat(value);
                }
            });
            
            console.log('已对', selectedItems.length, '个选中元素应用属性:', key, '=', value);
        } else {
            // 如果没有选中项，更新全局状态（用于新创建的元素）
            if (key === 'fillColor') {
                AppState.currentColor = new paper.Color(value);
            } else if (key === 'strokeWidth') {
                AppState.currentStrokeWidth = parseFloat(value);
            }
            
            console.log('已更新全局状态:', key, '=', value);
        }
        
        // 刷新视图
        paper.view.update();
    };

    // 设置QWebChannel通信桥梁
    function initializeQWebChannel() {
        if (typeof QWebChannel !== 'undefined') {
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pythonBridge = channel.objects.backend;
                console.log('QWebChannel initialized successfully');
            });
        } else {
            console.warn('QWebChannel not available');
        }
    }

    // 初始化通信
    initializeQWebChannel();

    // =============================================
    // == 鼠标和键盘事件处理
    // =============================================
    
    var isPanning = false;

    // 鼠标滚轮事件用于缩放
    canvas.addEventListener('wheel', function(event) {
        event.preventDefault();

        var oldZoom = paper.view.zoom;
        var mousePos = new paper.Point(event.offsetX, event.offsetY);
        var viewPos = paper.view.viewToProject(mousePos);

        var zoomFactor = 1.1;
        var newZoom = event.deltaY < 0 ? oldZoom * zoomFactor : oldZoom / zoomFactor;
        
        paper.view.zoom = newZoom;
        paper.view.center = viewPos.subtract(mousePos.subtract(paper.view.center).divide(newZoom / oldZoom));
    }, { passive: false });

    // 全局键盘事件监听器（用于平移）
    paper.view.onKeyDown = function(event) {
        if (event.key === 'space' && !isPanning) {
            isPanning = true;
            canvas.style.cursor = 'grab';
        }
    };

    paper.view.onKeyUp = function(event) {
        if (event.key === 'space') {
            isPanning = false;
            canvas.style.cursor = 'default';
        }
    };

    // 在当前活动工具的拖动事件中添加平移逻辑
    var originalMouseDragHandlers = {};
    
    // 为所有工具添加平移支持
    Object.keys(tools).forEach(function(toolName) {
        var tool = tools[toolName];
        if (tool.onMouseDrag) {
            originalMouseDragHandlers[toolName] = tool.onMouseDrag;
        }
        
        tool.onMouseDrag = function(event) {
            if (isPanning) {
                canvas.style.cursor = 'grabbing';
                paper.view.center = paper.view.center.subtract(event.delta);
            } else if (originalMouseDragHandlers[toolName]) {
                originalMouseDragHandlers[toolName](event);
            }
        };
    });

    console.log("Paper.js editor with tool management initialized successfully.");
});
