// 简易本地编辑器：基于 svgcanvas 构建最小 UI
// 依赖 CDN 中的 svgcanvas ESM 暴露

let canvas;
let svgroot;
let fallback = null; // 简易回退查看器

function getSvgCanvasCtor() {
  const g = window;
  // Try multiple global shapes: esbuild global, assigned module, default export
  const mod = g.svgcanvas || g.svgcanvas_global || {};
  
  // Try SvgCanvas class first, then default export, then whole module as constructor
  let Ctor = g.SvgCanvas || mod.SvgCanvas || mod.default;
  
  // If we have the module but no clear constructor, try the module itself
  if (!Ctor && mod && typeof mod === 'object') {
    // Check if the module has a constructor property or is callable
    Ctor = mod.constructor || mod;
  }
  
  return Ctor;
}

function init() {
  const Ctor = getSvgCanvasCtor();
  const container = document.getElementById('container');
  
  console.log('Available constructors:', { 
    'window.SvgCanvas': window.SvgCanvas, 
    'window.svgcanvas': window.svgcanvas,
    'Found constructor': Ctor 
  });
  
  if (Ctor) {
    try {
      // SvgCanvas 需要 container 和 config 参数
      const config = {
        dimensions: [800, 600],
        initFill: {
          color: '000000',
          opacity: 1
        },
        initStroke: {
          color: '000000',
          opacity: 1,
          width: 1
        },
        curConfig: {
          show_outside_canvas: true,
          selectNew: true,
          dimensions: [800, 600]
        }
      };
      
      canvas = new Ctor(container, config);
      console.log('SvgCanvas initialized successfully');
      
      // 测试基本功能
      if (canvas && typeof canvas.getSvgString === 'function') {
        console.log('SvgCanvas has getSvgString method');
      } else {
        console.warn('SvgCanvas missing getSvgString method');
      }
      
      if (canvas && typeof canvas.setSvgString === 'function') {
        console.log('SvgCanvas has setSvgString method');
      } else {
        console.warn('SvgCanvas missing setSvgString method');
      }
      
    } catch (e) {
      console.warn('new Ctor() failed:', e);
      try { 
        canvas = Ctor(container); 
        console.log('Ctor() (without new) succeeded');
      } catch (e2) { 
        console.warn('SvgCanvas 构造失败，使用回退模式', e, e2); 
      }
    }
  } else {
    console.warn('No SvgCanvas constructor found');
  }

  if (!canvas) {
    // 回退：最小预览器，仅支持 set/getSvgString
    fallback = {
      _svgText: '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"></svg>',
      setSvgString(txt) { this._svgText = String(txt || ''); container.innerHTML = this._svgText; },
      getSvgString() { return String(this._svgText || ''); }
    };
    fallback.setSvgString(fallback._svgText);
    return;
  }

  try { svgroot = canvas.getSvgRoot && canvas.getSvgRoot(); } catch {}
  // 初始视图 - 添加一些测试内容
  if (canvas.setSvgString) {
    const testSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
      <rect x="50" y="50" width="100" height="100" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
      <text x="100" y="200" text-anchor="middle" font-family="Arial" font-size="16" fill="#000">SVG 编辑器已就绪</text>
      <text x="100" y="220" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">按 R 键添加矩形，C 键添加圆形</text>
    </svg>`;
    canvas.setSvgString(testSvg);
    console.log('Test SVG loaded');
  } else {
    // 某些版本 API 不同，尝试直接写容器
    container.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><text x="100" y="100" font-family="Arial" font-size="16" fill="#000">SVG 编辑器初始化中...</text></svg>';
  }
  // 简单快捷键：R 画矩形，C 画圆，P 路径
  window.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 'r') {
      canvas.addSvgElementFromJson({
        element: 'rect', attr: { x: 50, y: 50, width: 120, height: 80, fill: '#e0e0e0', stroke: '#333' }
      });
    } else if (e.key.toLowerCase() === 'c') {
      canvas.addSvgElementFromJson({
        element: 'circle', attr: { cx: 200, cy: 200, r: 60, fill: 'none', stroke: '#1976d2' }
      });
    }
  });
}

window.addEventListener('DOMContentLoaded', init);

// Python 注入 SVG 字符串
window.svgEditorLoad = function (svgText) {
  try {
    if (canvas && canvas.setSvgString) {
      canvas.setSvgString(svgText);
    } else if (fallback) {
      fallback.setSvgString(svgText);
    }
  } catch (e) { console.error(e); }
};

// 可扩展：导出当前 SVG
window.svgEditorGet = function () {
  try {
    if (canvas && canvas.getSvgString) return canvas.getSvgString();
    if (fallback) return fallback.getSvgString();
    return '';
  } catch (e) { return ''; }
};
