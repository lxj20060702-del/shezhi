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
from qa import QA  # noqa: E402
from views import qa_view, recommend_view, graph_view, kb_view  # noqa: E402

st.set_page_config(page_title="她知 · 公益知识问答", page_icon="🌸", layout="wide")

# ---- 样式：统一放在 assets/style.css（🎨 设计同学改这里）----
st.markdown(f"<style>{(ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)

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

t_qa, t_rec, t_graph, t_kb = st.tabs(["💬 智能问答", "🎯 为你推荐", "🕸️ 知识图谱", "📚 知识库"])

with t_qa:
    qa_view.render(qa)
with t_rec:
    recommend_view.render()
with t_graph:
    graph_view.render()
with t_kb:
    kb_view.render(orgs, policies)
