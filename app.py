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
from recommend import recommend, summarize  # noqa: E402

st.set_page_config(page_title="她知 · 公益知识问答", page_icon="🌸", layout="wide")

st.markdown("""
<style>
.big-title{font-size:2rem;font-weight:800;margin-bottom:0}
.sub{color:#888;margin-top:0}
.src{background:#f6f8fa;border-left:3px solid #6da34d;padding:8px 12px;border-radius:6px;margin:6px 0;font-size:.9rem}
.rec{border:1px solid #e3e6ea;border-radius:10px;padding:12px 14px;margin:10px 0;background:#fff}
.rec-t{font-size:1.02rem;font-weight:700;margin-bottom:6px}
.rec-s{color:#6da34d;font-weight:600;font-size:.82rem;margin-left:6px}
.rec-line{font-size:.9rem;color:#333;margin:3px 0;line-height:1.5}
.rec-line code{background:#eef2f6;color:#2f6f9f;border-radius:4px;padding:1px 5px;font-size:.82rem}
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

tab1, tab_rec, tab2, tab3 = st.tabs(["💬 智能问答", "🎯 为你推荐", "🕸️ 知识图谱", "📚 知识库"])

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

with tab_rec:
    st.subheader("🎯 为你推荐")
    st.caption("说说你的情况，我们从公益组织库里帮你挑出「能帮上忙」的机构（按人群标签匹配，不含广告）")

    from recommend import JOB_OPTIONS, NEED_OPTIONS  # noqa: E402

    with st.form("rec_form"):
        c1, c2 = st.columns(2)
        gender = c1.radio("性别", ["女", "男", "不方便说"], horizontal=True)
        child = c2.radio("有孩子要在北京带着吗？", ["有", "没有"], horizontal=True)
        jobs = st.multiselect("你现在 / 最近做什么工作？（可多选，不确定可留空）", JOB_OPTIONS)
        needs = st.multiselect("最想解决的问题？（可多选，建议 1–2 个）", NEED_OPTIONS)
        go = st.form_submit_button("为我推荐", use_container_width=True)

    if go:
        st.session_state["rec_profile"] = {
            "gender": "" if gender == "不方便说" else gender,
            "jobs": jobs,
            "needs": needs,
            "has_child": child == "有",
        }

    profile = st.session_state.get("rec_profile")
    if not profile:
        st.info("先在上面选一选，然后点「为我推荐」👆　（不知道选什么也没关系，直接点按钮也能出结果）")
    else:
        res = recommend(profile)
        st.success(summarize(profile, res))
        if res["fallback"]:
            st.caption("没有精确命中标签，下面按「面向外来务工/流动人口的综合性机构」推荐。")

        for i, r in enumerate(res["orgs"], 1):
            o = r["item"]
            badges = " ".join(f"<code>{h}</code>" for h in r["reasons"][:6]) or "—"
            st.markdown(f"""
<div class="rec">
  <div class="rec-t">#{i} {o['name']}<span class="rec-s">匹配度 {r['score']}</span></div>
  <div class="rec-line">👥 <b>服务对象：</b>{o.get('target', '')}</div>
  <div class="rec-line">🧰 <b>能提供：</b>{'、'.join(o.get('services', []))}</div>
  <div class="rec-line">🎈 <b>主要活动：</b>{'、'.join(o.get('activities', [])[:6])}</div>
  <div class="rec-line">💡 <b>为什么推给你：</b>{badges}</div>
  <div class="rec-line">☎️ <b>联系方式：</b>{o.get('contact') or '见机构公开渠道'}　｜　📅 信息更新：{o.get('updated', '')}</div>
  <div class="rec-line">🔗 <b>来源：</b><a href="{o.get('source_url', '')}" target="_blank">{o.get('source_name', '')}</a></div>
</div>
""", unsafe_allow_html=True)

        if res["programs"]:
            st.markdown("##### 📌 相关的公益项目 / 计划")
            for r in res["programs"]:
                p = r["item"]
                st.markdown(
                    f"**{p['name']}**（{p.get('organizer', '')}，{p.get('since', '')}）<br>"
                    f"<span style='color:#666;font-size:.88rem'>{p.get('detail', '')}　"
                    f"来源：<a href=\"{p.get('source_url', '')}\" target=\"_blank\">{p.get('source_name', '')}</a></span>",
                    unsafe_allow_html=True)

        st.divider()
        st.caption("想了解**怎么办理**（法律援助怎么申请、孩子入学要什么材料），切到「💬 智能问答」问一句，答案带官方来源。")

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
    tpl = """
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
    html = (tpl
            .replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
            .replace("__EDGES__", json.dumps(edges, ensure_ascii=False)))
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
