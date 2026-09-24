# -*- coding: utf-8 -*-
"""🕸️ 知识图谱页

- 🎨 页面设计：容器/图例样式在 _inject_style；图谱 HTML 模板在 _GRAPH_TPL
- ⚙️ 功能实现：图谱数据来自 src/graph.py（实体/关系在 data/*.json 的 tags/services/activities）
"""
import json

import streamlit as st
import streamlit.components.v1 as components

from graph import build_graph

# 注意：这里用 __NODES__ / __EDGES__ 占位符替换，不要用 % 格式化
# （模板里 CSS 的 100% 会和 Python 的 % 格式化冲突）
_GRAPH_TPL = """
<style>
  .graph-wrap {
    border: 1px solid #e3e6ea;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    background: #fafbfc;
  }
  #net { width: 100%; height: 560px; }
</style>
<div class="graph-wrap"><div id="net"></div></div>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<script>
(function(){
  const nodes = new vis.DataSet(__NODES__);
  const edges = new vis.DataSet(__EDGES__);
  const groups = {
    "组织":    {color:{background:"#6da34d",border:"#5a8a3f"}, borderWidth:2},
    "项目":    {color:{background:"#e8a33d",border:"#c98a2e"}, borderWidth:2},
    "政策":    {color:{background:"#4a7ebb",border:"#3a6599"}, borderWidth:2},
    "服务":    {color:{background:"#9b7fd4",border:"#7d63b5"}, borderWidth:2},
    "人群标签":{color:{background:"#d46a6a",border:"#b55252"}, borderWidth:2}
  };
  const container = document.getElementById("net");
  const isMobile = window.innerWidth <= 640;
  // 手机端缩小高度并同步调整 iframe
  const netH = isMobile ? 420 : 560;
  container.style.height = netH + "px";
  try {
    const frame = window.frameElement;
    if (frame) frame.style.height = (netH + 24) + "px";
  } catch(e){}

  new vis.Network(container, {nodes:nodes, edges:edges}, {
    nodes:{
      shape:"dot",
      font:{size: isMobile?12:14, color:"#fff", face:"sans-serif",
            strokeWidth:2, strokeColor:"rgba(0,0,0,.25)"},
      scaling:{min: isMobile?10:8, max: isMobile?24:26},
      shadow:{enabled:true, color:"rgba(0,0,0,.18)", size:6}
    },
    edges:{
      color:{color:"#c4c9d0", highlight:"#6da34d"},
      font:{size: isMobile?9:10, align:"middle", color:"#777",
            strokeWidth:3, strokeColor:"#fff"},
      smooth:{type:"continuous"},
      arrows:{to:{enabled:true, scaleFactor:0.7}}
    },
    groups: groups,
    physics:{
      stabilization:true,
      barnesHut:{
        springLength: isMobile?110:140,
        gravitationalConstant:-3000,
        centralGravity:0.3
      }
    },
    interaction:{hover:true, dragNodes:true, dragView:true, zoomView:true}
  });
})();
</script>
"""


def _inject_style():
    """图谱页专属样式：图例 + 手机端适配。"""
    st.markdown("""
<style>
  .graph-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
    margin-top: 10px;
    font-size: .85rem;
    color: #555;
  }
  .graph-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .graph-legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    border: 1px solid rgba(0,0,0,.15);
  }
  .graph-meta {
    margin-top: 6px;
    color: #888;
    font-size: .8rem;
  }
  @media (max-width: 640px) {
    .graph-legend { font-size: .78rem; gap: 4px 14px; }
    .graph-legend-dot { width: 10px; height: 10px; }
    .graph-meta { font-size: .74rem; }
  }
</style>
""", unsafe_allow_html=True)


def render():
    _inject_style()
    st.subheader("公益服务知识图谱")
    st.caption("实体：组织 / 项目 / 政策 / 服务 / 人群标签　关系：提供 / 面向 / 适用")

    g = build_graph()
    nodes = [{"id": n["id"], "label": n["label"], "group": n["type"],
              "size": 24 if n["type"] in ("组织", "政策") else 17}
             for n in g["nodes"]]
    edges = [{"from": e["from"], "to": e["to"], "label": e["label"],
              "arrows": "to"} for e in g["edges"]]

    html = (_GRAPH_TPL
            .replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
            .replace("__EDGES__", json.dumps(edges, ensure_ascii=False)))
    components.html(html, height=600)

    legend_items = [
        ("#6da34d", "组织"),
        ("#e8a33d", "项目"),
        ("#4a7ebb", "政策"),
        ("#9b7fd4", "服务"),
        ("#d46a6a", "人群标签"),
    ]
    legend_html = "".join(
        f'<span class="graph-legend-item">'
        f'<span class="graph-legend-dot" style="background:{c}"></span>{name}</span>'
        for c, name in legend_items
    )
    st.markdown(
        f'<div class="graph-legend">{legend_html}</div>'
        f'<p class="graph-meta">当前 {len(nodes)} 个实体、{len(edges)} 条关系　｜　可拖拽节点、滚轮缩放</p>',
        unsafe_allow_html=True)
