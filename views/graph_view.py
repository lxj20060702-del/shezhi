# -*- coding: utf-8 -*-
"""🕸️ 知识图谱页

- 🎨 页面设计：改图例/容器高度/提示文案（HTML 模板在 _GRAPH_TPL）
- ⚙️ 功能实现：图谱数据来自 src/graph.py（实体/关系在 data/*.json 的 tags/services/activities）
"""
import json

import streamlit as st
import streamlit.components.v1 as components

from graph import build_graph

# 注意：这里用 __NODES__ / __EDGES__ 占位符替换，不要用 % 格式化
# （模板里 CSS 的 100% 会和 Python 的 % 格式化冲突）
_GRAPH_TPL = """
<div id="net" style="width:100%;height:560px;border:1px solid #ddd;border-radius:8px"></div>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<script>
const nodes = new vis.DataSet(__NODES__);
const edges = new vis.DataSet(__EDGES__);
const groups = {
  "组织":{color:"#6da34d"},"项目":{color:"#e8a33d"},"政策":{color:"#4a7ebb"},
  "服务":{color:"#9b7fd4"},"人群标签":{color:"#d46a6a"}
};
const container = document.getElementById("net");
new vis.Network(container, {nodes:nodes, edges:edges}, {
  nodes:{font:{size:14}, scaling:{min:8,max:26}},
  groups: groups,
  physics:{stabilization:true, barnesHut:{springLength:140}},
  interaction:{hover:true}
});
</script>
"""


def render():
    st.subheader("公益服务知识图谱")
    st.caption("实体：组织 / 项目 / 政策 / 服务 / 人群标签　关系：提供 / 面向 / 适用")

    g = build_graph()
    nodes = [{"id": n["id"], "label": n["label"], "group": n["type"], "shape": "dot",
              "size": 18 if n["type"] in ("组织", "政策") else 12}
             for n in g["nodes"]]
    edges = [{"from": e["from"], "to": e["to"], "label": e["label"], "arrows": "to",
              "font": {"size": 10, "align": "middle"}} for e in g["edges"]]

    html = (_GRAPH_TPL
            .replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
            .replace("__EDGES__", json.dumps(edges, ensure_ascii=False)))
    components.html(html, height=600)

    st.caption(f"图例：🟩组织 🟧项目 🟦政策 🟪服务 🟥人群标签　｜　当前 {len(nodes)} 个实体、{len(edges)} 条关系")
