# -*- coding: utf-8 -*-
"""views 包：每个标签页一个模块，便于多人并行开发（互不冲突）。

约定：每个模块暴露一个 render(...) 函数，由 app.py 调用。
- 🎨 页面设计：改 views/*.py 的结构与 assets/style.css
- ⚙️ 功能实现：改 src/*.py 与 data/*.json
"""
