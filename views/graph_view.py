# -*- coding: utf-8 -*-
"""🕸️ 知识图谱页

- 🎨 页面设计：改图例/容器高度/提示文案（HTML 模板在 _GRAPH_TPL）
- ⚙️ 功能实现：图谱数据来自 src/graph.py（实体/关系在 data/*.json 的 tags/services/activities）
"""
import json

import streamlit as st
import streamlit.components.v1 as components

from graph import build_graph

# ============================================================
# 🎨 图谱样式模板（粉色系柔和风格）
#   - 节点：大圆点 + 粉色渐变描边
#   - 线条：smooth 贝塞尔曲线 + 半透明粉色 + 柔和箭头
#   - 物理：更舒展的弹簧力，节点分布宽松优雅
# ============================================================
_GRAPH_TPL = """
<style>
  #net {
    width: 100%;
    height: 600px;
    border: none !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #fff8f9 0%, #fde8ec 50%, #fce4ea 100%) !important;
    box-shadow: 0 4px 24px rgba(201, 86, 118, 0.08), inset 0 1px 0 rgba(255,255,255,0.8) !important;
    overflow: hidden;
    position: relative;
  }
  #net::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 15% 20%, rgba(255,255,255,0.6) 0%, transparent 40%),
      radial-gradient(circle at 85% 80%, rgba(248,205,214,0.3) 0%, transparent 45%);
    pointer-events: none;
    z-index: 0;
  }
  .vis-network {
    z-index: 1;
  }
</style>
<div id="net"></div>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<script>
const nodes = new vis.DataSet(__NODES__);
const edges = new vis.DataSet(__EDGES__);

// 🌸 粉色系节点配色（柔和、温暖、女性向）
const groups = {
  "组织":    { color: { background: "#e07f97", border: "#c95676", highlight: { background: "#f0a8b7", border: "#c95676" } } },
  "项目":    { color: { background: "#f0a8b7", border: "#e07f97", highlight: { background: "#f8cdd6", border: "#e07f97" } } },
  "政策":    { color: { background: "#f5b8c5", border: "#e07f97", highlight: { background: "#f8d3dc", border: "#e07f97" } } },
  "服务":    { color: { background: "#c99ab5", border: "#a57090", highlight: { background: "#d4adc3", border: "#a57090" } } },
  "人群标签":{ color: { background: "#b885a8", border: "#8e6082", highlight: { background: "#c99ab5", border: "#8e6082" } } }
};

const container = document.getElementById("net");
const network = new vis.Network(container, {nodes:nodes, edges:edges}, {
  // —— 节点：大、圆润、柔和 ——
  nodes: {
    font: {
      size: 14,
      face: "system-ui, 'PingFang SC', sans-serif",
      color: "#3d3530",
      strokeWidth: 3,
      strokeColor: "rgba(255,255,255,0.85)"
    },
    shape: "circle",
    borderWidth: 2.5,
    shadow: { enabled: true, color: "rgba(201,86,118,0.18)", size: 12, x: 0, y: 4 },
    scaling: { min: 14, max: 34 }
  },
  groups: groups,

  // —— 线条：柔和贝塞尔曲线 ——
  edges: {
    smooth: {
      enabled: true,
      type: "cubicBezier",
      forceDirection: "horizontal",
      roundness: 0.5,
      undirected: false
    },
    color: { color: "rgba(201,86,118,0.45)", highlight: "#c95676", hover: "#e07f97" },
    width: 1.8,
    hoverWidth: 2.8,
    selectionWidth: 2.5,
    arrows: {
      to: { enabled: true, scaleFactor: 0.7 }
    },
    arrowStrikethrough: false,
    font: {
      size: 11,
      color: "#8a7d74",
      face: "system-ui, sans-serif",
      strokeWidth: 4,
      strokeColor: "rgba(255,255,255,0.85)",
      align: "middle"
    }
  },

  // —— 物理：舒展优雅，不挤 ——
  physics: {
    stabilization: { enabled: true, iterations: 200 },
    barnesHut: {
      gravitationalConstant: -3200,
      centralGravity: 0.35,
      springLength: 160,
      springConstant: 0.06,
      damping: 0.08
    },
    minVelocity: 0.75,
    solver: "barnesHut"
  },

  // —— 交互：丝滑 hover ——
  interaction: {
    hover: true,
    tooltipDelay: 120,
    zoomView: true,
    dragView: true
  }
});
</script>
"""


def render():
    st.subheader("🕸️ 公益服务知识图谱")
    st.caption("实体：组织 / 项目 / 政策 / 服务 / 人群标签　关系：提供 / 面向 / 适用")

    g = build_graph()
    nodes = [
        {
            "id": n["id"],
            "label": n["label"],
            "group": n["type"],
            "shape": "circle",
            "size": 28 if n["type"] in ("组织", "政策") else 20,
            "title": f"{n['label']}（{n['type']}）"
        }
        for n in g["nodes"]
    ]
    edges = [
        {
            "from": e["from"],
            "to": e["to"],
            "label": e["label"],
            "arrows": "to",
            "smooth": {"type": "cubicBezier", "roundness": 0.5}
        }
        for e in g["edges"]
    ]

    html = (_GRAPH_TPL
            .replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
            .replace("__EDGES__", json.dumps(edges, ensure_ascii=False)))
    components.html(html, height=640)

    st.markdown(
        '<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:4px;font-size:.82rem;color:#8a7d74">'
        '<span>🩷 <b style="color:#e07f97">组织</b></span>'
        '<span>🌸 <b style="color:#f0a8b7">项目</b></span>'
        '<span>🌷 <b style="color:#f5b8c5">政策</b></span>'
        '<span>💜 <b style="color:#c99ab5">服务</b></span>'
        '<span>✨ <b style="color:#b885a8">人群标签</b></span>'
        f'<span style="margin-left:auto">{len(nodes)} 实体 · {len(edges)} 关系</span>'
        '</div>',
        unsafe_allow_html=True
    )
