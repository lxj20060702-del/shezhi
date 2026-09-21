# -*- coding: utf-8 -*-
"""🎯 为你推荐页（功能模块②：组织与活动个性化推荐）

- 🎨 页面设计：改表单布局与卡片样式（卡片 HTML 在 _card_html，样式在 assets/style.css 的 .rec*）
- ⚙️ 功能实现：匹配算法在 src/recommend.py；数据在 data/organizations.json
"""
import streamlit as st

from recommend import recommend, summarize, JOB_OPTIONS, NEED_OPTIONS


def _card_html(idx, r):
    o = r["item"]
    badges = " ".join(f"<code>{h}</code>" for h in r["reasons"][:6]) or "—"
    return f"""
<div class="rec">
  <div class="rec-t">#{idx} {o['name']}<span class="rec-s">匹配度 {r['score']}</span></div>
  <div class="rec-line">👥 <b>服务对象：</b>{o.get('target', '')}</div>
  <div class="rec-line">🧰 <b>能提供：</b>{'、'.join(o.get('services', []))}</div>
  <div class="rec-line">🎈 <b>主要活动：</b>{'、'.join(o.get('activities', [])[:6])}</div>
  <div class="rec-line">💡 <b>为什么推给你：</b>{badges}</div>
  <div class="rec-line">☎️ <b>联系方式：</b>{o.get('contact') or '见机构公开渠道'}　｜　📅 信息更新：{o.get('updated', '')}</div>
  <div class="rec-line">🔗 <b>来源：</b><a href="{o.get('source_url', '')}" target="_blank">{o.get('source_name', '')}</a></div>
</div>
"""


def render():
    st.subheader("🎯 为你推荐")
    st.caption("说说你的情况，我们从公益组织库里帮你挑出「能帮上忙」的机构（按人群标签匹配，不含广告）")

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
        return

    res = recommend(profile)
    st.success(summarize(profile, res))
    if res["fallback"]:
        st.caption("没有精确命中标签，下面按「面向外来务工/流动人口的综合性机构」推荐。")

    for i, r in enumerate(res["orgs"], 1):
        st.markdown(_card_html(i, r), unsafe_allow_html=True)

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
