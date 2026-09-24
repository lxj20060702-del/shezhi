# -*- coding: utf-8 -*-
"""🕸️ 知识图谱页

- 🎨 页面设计：容器/图例样式在 _inject_style；图谱 HTML 模板在 _GRAPH_TPL
- ⚙️ 功能实现：图谱数据来自 src/graph.py（实体/关系在 data/*.json 的 tags/services/activities）
"""
import json

import streamlit as st
import streamlit.components.v1 as components

from graph import build_graph

_GRAPH_TPL = """
<style>
  .graph-wrap {
    border: 1px solid #e0e8ec;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(116,169,197,.10), 0 1px 3px rgba(0,0,0,.04);
    background: linear-gradient(135deg, #f5f9fc 0%, #fdf6f4 100%);
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
    "组织":    {color:{background:"#74A9C5",border:"#5a8fae",highlight:{background:"#74A9C5",border:"#3d7291"},hover:{background:"#74A9C5",border:"#5a8fae"}}, borderWidth:2, opacity:0.82},
    "项目":    {color:{background:"#EDDDAB",border:"#d4c089",highlight:{background:"#EDDDAB",border:"#b89f60"},hover:{background:"#EDDDAB",border:"#d4c089"}}, borderWidth:2, opacity:0.82},
    "政策":    {color:{background:"#C2E5CF",border:"#9dcaaf",highlight:{background:"#C2E5CF",border:"#76ad8c"},hover:{background:"#C2E5CF",border:"#9dcaaf"}}, borderWidth:2, opacity:0.82},
    "服务":    {color:{background:"#F2B8AE",border:"#d9968b",highlight:{background:"#F2B8AE",border:"#bf7368"},hover:{background:"#F2B8AE",border:"#d9968b"}}, borderWidth:2, opacity:0.82},
    "人群标签":{color:{background:"#DD7389",border:"#c2566d",highlight:{background:"#DD7389",border:"#9e3d54"},hover:{background:"#DD7389",border:"#c2566d"}}, borderWidth:2, opacity:0.82}
  };
  const container = document.getElementById("net");
  const isMobile = window.innerWidth <= 640;
  const netH = isMobile ? 420 : 560;
  container.style.height = netH + "px";
  try {
    const frame = window.frameElement;
    if (frame) frame.style.height = (netH + 24) + "px";
  } catch(e){}

  const network = new vis.Network(container, {nodes:nodes, edges:edges}, {
    nodes:{
      shape:"dot",
      font:{size: isMobile?12:14, color:"#3a4a4d", face:"sans-serif",
            strokeWidth:3, strokeColor:"rgba(255,255,255,.85)"},
      scaling:{min: isMobile?10:8, max: isMobile?24:26},
      shadow:{enabled:true, color:"rgba(80,90,100,.38)", size:14, x:0, y:8}
    },
    edges:{
      color:{color:"rgba(194,229,207,.65)", highlight:"#74A9C5", hover:"#C2E5CF"},
      font:{size: isMobile?9:10, align:"middle", color:"#7a8a8d",
            strokeWidth:3, strokeColor:"rgba(255,255,255,.9)"},
      smooth:{type:"continuous"},
      arrows:{to:{enabled:true, scaleFactor:0.7}}
    },
    groups: groups,
    physics:{
      stabilization:true,
      barnesHut:{
        springLength: isMobile?110:140,
        gravitationalConstant:-3000,
        centralGravity:0.45
      }
    },
    interaction:{hover:true, dragNodes:true, dragView:true, zoomView:true}
  });

  network.once("stabilizationIterationsDone", function() {
    network.fit({animation: {duration: 600, easingFunction: "easeInOutQuad"}});
  });
})();
</script>
"""


def _inject_style():
    """图谱页专属样式：统计卡片 + 图例 + 提示区块 + 手机端适配。"""
    st.markdown("""
<style>
  .graph-stats {
    display: flex;
    gap: 12px;
    margin: 0 0 16px;
    flex-wrap: wrap;
  }
  .graph-stat-card {
    flex: 1;
    min-width: 110px;
    background: #fff;
    border: 1px solid #e0e8ec;
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(116,169,197,.08);
    position: relative;
    overflow: hidden;
  }
  .graph-stat-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
  }
  .graph-stat-card:nth-child(1)::before { background: #74A9C5; }
  .graph-stat-card:nth-child(2)::before { background: #DD7389; }
  .graph-stat-card:nth-child(3)::before { background: #C2E5CF; }
  .graph-stat-num {
    font-size: 1.6rem;
    font-weight: 800;
    color: #3a4a4d;
    line-height: 1.2;
  }
  .graph-stat-label {
    font-size: .8rem;
    color: #8899a0;
    margin-top: 2px;
  }

  .graph-legend-wrap {
    background: linear-gradient(135deg, #f7fbfc 0%, #fdf6f4 100%);
    border: 1px solid #e0e8ec;
    border-radius: 12px;
    padding: 12px 18px;
    margin-top: 14px;
  }
  .graph-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
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
    border: 1.5px solid rgba(0,0,0,.12);
    box-shadow: inset 0 1px 2px rgba(255,255,255,.5), 0 1px 2px rgba(0,0,0,.08);
  }

  .graph-tips {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
  }
  .graph-tip-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #fff;
    border: 1px solid #e0e8ec;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: .82rem;
    color: #6a7a7d;
  }
  .graph-tip-icon {
    font-size: 1rem;
  }

  .graph-meta {
    margin-top: 10px;
    color: #8899a0;
    font-size: .8rem;
  }
  @media (max-width: 640px) {
    .graph-stats { gap: 8px; margin-bottom: 12px; }
    .graph-stat-card { padding: 10px 6px; min-width: 0; flex: 1 1 30%; border-radius: 10px; }
    .graph-stat-num { font-size: 1.25rem; }
    .graph-stat-label { font-size: .7rem; margin-top: 1px; }
    .graph-stat-card::before { height: 2.5px; }
    .graph-wrap { border-radius: 12px; }
    .graph-legend-wrap { padding: 10px 12px; margin-top: 10px; border-radius: 10px; }
    .graph-legend { font-size: .76rem; gap: 4px 12px; }
    .graph-legend-item { gap: 4px; }
    .graph-legend-dot { width: 9px; height: 9px; border-width: 1px; }
    .graph-tips { gap: 6px; margin-top: 10px; }
    .graph-tip-item { font-size: .7rem; padding: 3px 10px; gap: 4px; }
    .graph-tip-icon { font-size: .85rem; }
    .graph-meta { font-size: .72rem; margin-top: 8px; line-height: 1.5; }
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

    org_count = sum(1 for n in g["nodes"] if n["type"] == "组织")
    st.markdown(f"""
<div class="graph-stats">
  <div class="graph-stat-card">
    <div class="graph-stat-num">{len(nodes)}</div>
    <div class="graph-stat-label">实体总数</div>
  </div>
  <div class="graph-stat-card">
    <div class="graph-stat-num">{len(edges)}</div>
    <div class="graph-stat-label">关系总数</div>
  </div>
  <div class="graph-stat-card">
    <div class="graph-stat-num">{org_count}</div>
    <div class="graph-stat-label">公益组织</div>
  </div>
</div>
""", unsafe_allow_html=True)

    html = (_GRAPH_TPL
            .replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
            .replace("__EDGES__", json.dumps(edges, ensure_ascii=False)))
    components.html(html, height=600)

    legend_items = [
        ("#74A9C5", "组织"),
        ("#EDDDAB", "项目"),
        ("#C2E5CF", "政策"),
        ("#F2B8AE", "服务"),
        ("#DD7389", "人群标签"),
    ]
    legend_html = "".join(
        f'<span class="graph-legend-item">'
        f'<span class="graph-legend-dot" style="background:{c}"></span>{name}</span>'
        for c, name in legend_items
    )
    st.markdown(
        f'<div class="graph-legend-wrap"><div class="graph-legend">{legend_html}</div>'
        f'<div class="graph-tips">'
        f'<span class="graph-tip-item"><span class="graph-tip-icon">🖱️</span>拖拽节点</span>'
        f'<span class="graph-tip-item"><span class="graph-tip-icon">🔍</span>滚轮缩放</span>'
        f'<span class="graph-tip-item"><span class="graph-tip-icon">👆</span>悬停高亮</span>'
        f'</div></div>'
        f'<p class="graph-meta">当前 {len(nodes)} 个实体、{len(edges)} 条关系　｜　数据来源：北京市妇联/公益组织公开脱敏资料</p>',
        unsafe_allow_html=True)
