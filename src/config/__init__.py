"""
配置模块
========

包含项目的配置和路径管理。
"""

from .paths import paths, get_potrace_path, get_mkbitmap_path, get_trace_path, get_tracegui_path, get_vtracer_path

__all__ = [
    'paths', 
    'get_potrace_path', 
    'get_mkbitmap_path', 
    'get_trace_path', 
    'get_tracegui_path', 
    'get_vtracer_path'
]
