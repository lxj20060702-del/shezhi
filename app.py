# -*- coding: utf-8 -*-
"""“她知” —— 面向北京流动女性的公益垂直知识问答系统（Streamlit 界面）。"""
import json
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import kb  # noqa: E402
from qa import QA  # noqa: E402
from graph import build_graph  # noqa: E402

st.set_page_config(page_title="她知 · 公益知识问答", page_icon="🌸", layout="wide")

st.markdown("""
<style>
.big-title{font-size:2rem;font-weight:800;margin-bottom:0}
.sub{color:#888;margin-top:0}
.src{background:#f6f8fa;border-left:3px solid #6da34d;padding:8px 12px;border-radius:6px;margin:6px 0;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🌸 她知</p>', unsafe_allow_html=True)
st.markdown('<p class="sub">面向北京流动女性的公益垂直知识问答系统 · 政策与公益资源可溯源</p>',
            unsafe_allow_html=True)


@st.cache_resource
def get_qa():
    return QA()


qa = get_qa()
orgs, programs = kb.get_orgs_and_programs()
policies = kb.get_policies()

with st.sidebar:
    st.header("ℹ️ 系统信息")
    st.write(f"知识库：组织 {len(orgs)} 家 · 项目 {len(programs)} 个 · 政策 {len(policies)} 条")
    st.write("大模型：" + ("✅ " + str(qa.llm.model) if qa.llm.available else "⚠️ 未配置（检索式降级）"))
    st.caption("数据源：北京市妇联/公益组织公开脱敏资料、政府权威政策（gov.cn 等）")
    st.divider()
    st.caption("免费方案：GLM-4-Flash / 硅基流动；检索层本地 BM25（jieba）。")

tab1, tab2, tab3 = st.tabs(["💬 智能问答", "🕸️ 知识图谱", "📚 知识库"])

with tab1:
    st.subheader("试试这样问：")
    c1, c2, c3 = st.columns(3)
    example = None
    if c1.button("外地务工人员在北京怎么申请免费法律援助？", use_container_width=True):
        example = "外地务工人员在北京怎么申请免费法律援助？"
    if c2.button("孩子在京上学需要什么材料？", use_container_width=True):
        example = "孩子在京上学需要什么材料？"
    if c3.button("有哪些服务流动女性的公益组织？办过什么文艺活动？", use_container_width=True):
        example = "有哪些服务流动女性的公益组织？办过什么文艺活动？"

    q = st.chat_input("输入你的问题…")
    if example:
        q = example
    if q:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            with st.spinner("检索知识库中…"):
                res = qa.answer(q)
            st.markdown(res["answer"])
            st.caption(f"路由：{res['route']}库 · 模式：{res['mode']}")
            with st.expander("🔍 查看依据（可溯源）"):
                for i, d in enumerate(res["sources"]):
                    st.markdown(
                        f'<div class="src"><b>【来源{i+1}】{d["title"]}</b>　'
                        f'<span style="color:#888">{d["type"]}</span><br>'
                        f'{d["source_name"]} · <a href="{d["source_url"]}" target="_blank">{d["source_url"]}</a><br>'
                        f'<span style="color:#888">更新：{d["updated"]}</span></div>',
                        unsafe_allow_html=True)

with tab2:
    st.subheader("公益服务知识图谱")
    st.caption("实体：组织 / 项目 / 政策 / 服务 / 人群标签　关系：提供 / 面向 / 适用")
    g = build_graph()
    color = {"组织": "#6da34d", "项目": "#e8a33d", "政策": "#4a7ebb", "服务": "#9b7fd4", "人群标签": "#d46a6a"}
    nodes = [{"id": n["id"], "label": n["label"], "group": n["type"], "shape": "dot",
              "size": 18 if n["type"] in ("组织", "政策") else 12}
             for n in g["nodes"]]
    edges = [{"from": e["from"], "to": e["to"], "label": e["label"], "arrows": "to",
              "font": {"size": 10, "align": "middle"}} for e in g["edges"]]
    html = """
    <div id="net" style="width:100%;height:560px;border:1px solid #ddd;border-radius:8px"></div>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script>
    const nodes = new vis.DataSet(%s);
    const edges = new vis.DataSet(%s);
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
    """ % (json.dumps(nodes, ensure_ascii=False), json.dumps(edges, ensure_ascii=False))
    components.html(html, height=600)
    st.caption("图例：🟩组织 🟧项目 🟦政策 🟪服务 🟥人群标签")

with tab3:
    st.subheader("公益组织库")
    st.dataframe([{"名称": o["name"], "服务对象": o["target"],
                   "核心服务/活动": "、".join(o.get("services", []) + o.get("activities", []))[:60],
                   "来源": o["source_name"]} for o in orgs], use_container_width=True)
    st.subheader("政策知识库")
    st.dataframe([{"主题": p["topic"], "标题": p["title"], "发布机构": p["publisher"],
                   "生效/更新": p.get("effective_date", "") or p["updated"]} for p in policies],
                 use_container_width=True)
