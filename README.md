# RasterVectorStudio - 位图转矢量与本地SVG编辑器

一个功能强大的位图到矢量图转换和SVG编辑工具，集成了多种矢量化引擎和基于Paper.js的实时编辑功能。

## 🌟 主要功能

### 矢量化转换
- **多引擎支持**：集成5种不同的矢量化引擎
  - `mkbitmap+potrace`：经典的位图预处理+路径追踪组合
  - `mkbitmap`：专业位图预处理工具
  - `potrace`：高质量路径追踪算法
  - `Trace(.NET)`：基于.NET的矢量化引擎
  - `vtracer`：现代化的Rust矢量化工具

- **智能参数调节**：
  - 阈值调节（0-255）
  - 噪点过滤（turdsize）
  - 平滑度控制（alphamax）
  - 边缘检测模式
  - 滤波半径和缩放因子
  - 转弯策略和优化容差

### SVG编辑功能
- **实时预览**：基于Paper.js的高性能Canvas渲染
- **多种工具**：
  - 🔍 **选择工具**：选中和移动SVG元素
  - ✏️ **画笔工具**：自由绘制路径
  - ⭕ **形状工具**：绘制几何形状
  - 💧 **吸管工具**：从原图中拾取颜色
  - 🪣 **填充工具**：区域颜色填充
  - 🧽 **擦除工具**：删除元素

### 颜色编辑系统
- **智能颜色选择**：
  - 填充颜色选择和修改
  - 描边颜色选择和修改
  - 描边宽度调节
- **颜色拾取**：从左侧原图预览中吸取任意颜色
- **实时应用**：选中元素后可立即修改颜色属性

### 用户界面
- **双面板设计**：
  - 左侧：原图预览 + 参数设置
  - 右侧：SVG编辑器（支持文本编辑和可视化编辑）
- **智能缩放**：支持图片放大、缩小、适应窗口
- **模式切换**：转换工具模式 ↔ 绘画工具模式

## 🛠️ 系统要求

- **操作系统**：Windows 10/11
- **Python**：3.8+
- **依赖包**：
  - PyQt5 / PyQt6
  - QWebEngine
  - Pillow
  - pathlib

## 📦 安装和使用

### 方式1：直接运行可执行文件
1. 下载 `dist/RasterVectorStudio.exe`
2. 双击运行即可

### 方式2：源码运行
1. 克隆项目：
```bash
git clone [项目地址]
cd RasterVectorStudio
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python start.py
```

### 方式3：打包为可执行文件
```bash
python build_config.py
pyinstaller --clean RasterVectorStudio.spec
```

## 🎯 使用指南

### 矢量化流程
1. **打开位图**：点击 "📁 打开位图" 选择要转换的图片
2. **选择引擎**：在参数面板中选择合适的矢量化引擎
3. **调节参数**：根据图片特点调整相关参数
4. **开始转换**：点击 "⚡ 开始矢量化" 按钮
5. **预览结果**：在右侧编辑器中查看转换结果
6. **保存文件**：点击 "💾 另存SVG" 保存结果

### 编辑功能
1. **选择模式**：点击左侧 "🎨 绘画工具" 切换到编辑模式
2. **选择工具**：从工具栏选择需要的编辑工具
3. **颜色操作**：
   - 使用吸管工具从原图吸取颜色
   - 点击填充/描边颜色按钮手动选择颜色
   - 选中元素后自动应用颜色
4. **实时编辑**：在右侧Paper.js画布上直接编辑SVG

## 🏗️ 技术架构

### 核心技术栈
- **前端渲染**：Paper.js + HTML5 Canvas
- **后端框架**：PyQt5 + QWebEngine
- **通信机制**：QWebChannel（Python ↔ JavaScript）
- **矢量化引擎**：多引擎适配器模式

### 架构设计
```
PyQt5 UI Layer (总指挥)
    ↓ QWebChannel
JavaScript/Paper.js (执行层)
    ↓ 适配器模式
多矢量化引擎 (工具层)
```

### 关键组件
- `src/gui/main_window.py`：主窗口和UI管理
- `src/gui/editor_widget.py`：Web编辑器组件
- `src/tools/`：各种矢量化引擎适配器
- `web/paperjs_editor_pro.js`：Paper.js编辑器核心
- `web/paperjs_editor_pro.html`：编辑器页面

## 📁 项目结构

```
RasterVectorStudio/
├── src/
│   ├── gui/                 # UI组件
│   │   ├── main_window.py   # 主窗口
│   │   ├── editor_widget.py # 编辑器组件
│   │   └── styles.qss       # 样式表
│   ├── tools/               # 矢量化工具
│   │   ├── potrace_adapter.py
│   │   ├── trace_adapter.py
│   │   └── vtracer_adapter.py
│   └── config/              # 配置管理
│       └── paths.py
├── web/                     # Web编辑器
│   ├── paperjs_editor_pro.html
│   └── paperjs_editor_pro.js
├── external_tools/          # 外部工具
│   ├── potrace-1.16.win64/
│   ├── autotrace-0.31.10/
│   └── vtracer-0.6.4/
├── dist/                    # 打包输出
├── start.py                 # 程序入口
├── build_config.py          # 打包配置
└── RasterVectorStudio.spec  # PyInstaller配置
```

## 🎨 支持的文件格式

### 输入格式
- **位图**：PNG, JPG, JPEG, BMP, GIF, TIFF
- **SVG**：标准SVG文件（用于编辑）

### 输出格式
- **SVG**：可缩放矢量图形
- **其他**：通过各引擎支持多种矢量格式

## 🔧 高级功能

### 引擎特色
- **potrace系列**：最适合黑白线稿和简单图形
- **vtracer**：适合彩色图片和复杂图像
- **autotrace**：提供多种输出格式选择

### 编辑特色
- **Paper.js集成**：专业级矢量图编辑体验
- **实时预览**：所见即所得的编辑效果
- **智能颜色管理**：Python-JavaScript双向通信

## 🐛 已知问题

- QWebChannel在初始化时会产生一些属性警告（不影响功能）
- 某些复杂SVG在Paper.js中可能需要额外处理
- 大型图片转换时可能需要较长时间

## 🚀 后续计划

- [ ] 增加更多绘图工具
- [ ] 支持图层管理
- [ ] 添加撤销/重做功能
- [ ] 优化大文件处理性能
- [ ] 增加批量处理功能

## 📄 许可证

本项目采用 MIT 许可证，详情请查看 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个项目！

---

*RasterVectorStudio - 让位图转矢量变得简单而强大*
