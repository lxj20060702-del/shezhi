# -*- coding: utf-8 -*-
"""「她知」—— 面向北京流动女性的公益垂直知识问答系统（Streamlit 入口）。

====================== 4 人分工看这里 ======================
目录地图（谁改哪里）：
  app.py            入口接线：页面配置 / 加载样式 / 侧边栏 / 标签页分发
                    ⚠️ 尽量少改；加了新页面才动它
  assets/style.css  全站样式（配色、卡片、字号、手机适配）   ← 🎨 页面设计
  views/*.py        每个标签页一个文件，各管一个，互不冲突     ← 🎨 页面设计
  src/*.py          检索 / 问答 / 图谱 / 推荐 等业务逻辑      ← ⚙️ 功能实现
  data/*.json       知识库数据（组织/项目/政策）             ← ⚙️ 功能实现
  tests/smoke_test.py  冒烟测试：改完跑一下，能提前发现报错
===========================================================
"""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import kb  # noqa: E402
from src.qa import QA  # noqa: E402
from views import qa_view, recommend_view, graph_view, kb_view  # noqa: E402

st.set_page_config(page_title="她知 · 公益知识问答", page_icon="🌸", layout="wide")

# ---- 样式：统一放在 assets/style.css（🎨 设计同学改这里）----
st.markdown(f"<style>{(ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)

st.markdown('<p class="big-title">🌸 她知</p>', unsafe_allow_html=True)
st.markdown('<p class="sub">面向北京流动女性的公益垂直知识问答系统</p>',
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

# 组织详情展示（点击知识库地图中的组织名称后，跨标签页显示）
selected_org_id = st.query_params.get("selected_org", None)
if selected_org_id:
    if isinstance(selected_org_id, list):
        selected_org_id = selected_org_id[0]
    org = next((o for o in orgs if o["id"] == selected_org_id), None)
    if org:
        st.markdown("---")
        st.markdown(f"### 🏢 {org['name']}")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"**简介**：{org.get('intro', '')}")
            st.markdown(f"**服务对象**：{org.get('target', '')}")
            services = org.get("services", [])
            if services:
                st.markdown(f"**核心服务**：{'、'.join(services)}")
            activities = org.get("activities", [])
            if activities:
                st.markdown(f"**工作/活动**：{'、'.join(activities)}")
            if org.get("founded"):
                st.markdown(f"**成立背景**：{org['founded']}")
            if org.get("join"):
                st.markdown(f"**如何参与**：{org['join']}")
        with col2:
            if org.get("tags"):
                st.markdown("**标签**")
                tag_html = " ".join(
                    f'<span class="org-tag">{t}</span>' for t in org["tags"]
                )
                st.markdown(f'<div class="org-tags">{tag_html}</div>',
                            unsafe_allow_html=True)
            if org.get("contact") and org["contact"] != "见机构公开渠道":
                st.markdown(f"📞 **联系方式**：{org['contact']}")
            if org.get("source_url"):
                st.markdown(f"📚 [了解更多（来源：{org.get('source_name', '')}）]({org['source_url']})")
        if st.button("← 返回地图", key="back_to_map"):
            st.query_params.clear()
            st.rerun()

t_qa, t_rec, t_graph, t_kb = st.tabs(["💬 智能问答", "🎯 为你推荐", "🕸️ 知识图谱", "📚 知识库"])

with t_qa:
    qa_view.render(qa)
with t_rec:
    recommend_view.render()
with t_graph:
    graph_view.render()
with t_kb:
    kb_view.render(orgs, policies)
