# 将 @svgedit/svgcanvas 打包为单文件 bundle.js 到 web/vendor/svgcanvas/
# 依赖：Node.js、npm、esbuild

param(
  [string]$ProjectRoot = (Resolve-Path ".."),
  [string]$OutDir = (Join-Path (Resolve-Path "..") "web/vendor/svgcanvas")
)

$ErrorActionPreference = 'Stop'

Write-Host "ProjectRoot: $ProjectRoot"
Write-Host "OutDir: $OutDir"

# 初始化临时目录
$work = Join-Path $ProjectRoot ".offline_svgcanvas"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $work | Out-Null
Push-Location $work

# 生成最小打包入口 index.js
@'
import * as svgcanvas from "@svgedit/svgcanvas";
// 通用全局导出，兼容不同打包姿势
window.svgcanvas = svgcanvas;
window.SvgCanvas = svgcanvas.default || svgcanvas.SvgCanvas || svgcanvas;
'@ | Set-Content -Encoding UTF8 -Path index.js

# 初始化 npm 并安装依赖
if (-not (Test-Path (Join-Path $work "package.json"))) {
  npm init -y | Out-Null
}

npm install @svgedit/svgcanvas esbuild --no-audit --no-fund

# 运行 esbuild 进行打包
$bundle = Join-Path $OutDir "bundle.js"
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

npx esbuild index.js --bundle --format=iife --global-name=svgcanvas_global --outfile=$bundle

Pop-Location
Write-Host "打包完成: $bundle"
