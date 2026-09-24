# -*- coding: utf-8 -*-
"""🎯 为你推荐页（功能模块②：组织与活动个性化推荐）

- 🎨 页面设计：卡片样式与手机端适配在 _inject_style；卡片 HTML 在 _card_html
- ⚙️ 功能实现：匹配算法在 src/recommend.py；数据在 data/organizations.json
"""
import streamlit as st

from recommend import recommend, summarize, JOB_OPTIONS, NEED_OPTIONS


def _inject_style():
    """推荐页专属样式 + 手机端适配（仅作用于本页，不影响其他页面）。"""
    st.markdown("""
<style>
/* ---------- 推荐卡片 ---------- */
.rec {
  border: 1px solid var(--line, #e3e6ea);
  border-radius: 14px;
  padding: 16px 18px;
  margin: 12px 0;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.03);
  transition: box-shadow .2s ease, transform .2s ease;
}
.rec:hover {
  box-shadow: 0 4px 16px rgba(109,163,77,.14);
  transform: translateY(-1px);
}
.rec-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.rec-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--brand, #6da34d);
  color: #fff;
  font-size: .82rem;
  font-weight: 700;
  flex-shrink: 0;
}
.rec-name {
  font-size: 1.08rem;
  font-weight: 700;
  color: var(--ink, #222);
  flex: 1;
  min-width: 0;
}
.rec-score {
  background: var(--brand-soft, #f2f7ee);
  color: var(--brand, #6da34d);
  border-radius: 999px;
  padding: 2px 10px;
  font-size: .78rem;
  font-weight: 600;
  white-space: nowrap;
}
.rec-line {
  font-size: .9rem;
  color: #333;
  margin: 5px 0;
  line-height: 1.6;
  display: flex;
  gap: 6px;
}
.rec-line b {
  color: var(--ink-soft, #666);
  font-weight: 600;
  flex-shrink: 0;
}
.rec-line code {
  background: #eef2f6;
  color: #2f6f9f;
  border-radius: 4px;
  padding: 1px 6px;
  font-size: .82rem;
  margin: 1px 2px;
}
.rec-foot {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--line, #e3e6ea);
  font-size: .82rem;
  color: var(--ink-soft, #666);
  line-height: 1.6;
}
.rec-foot a {
  color: var(--brand, #6da34d);
  text-decoration: none;
}
.rec-foot a:hover {
  text-decoration: underline;
}

/* ---------- 手机端（≤640px） ---------- */
@media (max-width: 640px) {
  .rec { padding: 12px 14px; margin: 10px 0; border-radius: 12px; }
  .rec-name { font-size: 1rem; }
  .rec-line { font-size: .86rem; margin: 4px 0; }
  .rec-score { font-size: .74rem; padding: 2px 8px; }
  .rec-rank { min-width: 22px; height: 22px; font-size: .74rem; }
  .rec-foot { font-size: .78rem; }
}
</style>
""", unsafe_allow_html=True)


def _card_html(idx, r):
    o = r["item"]
    badges = " ".join(f"<code>{h}</code>" for h in r["reasons"][:6]) or "—"
    services = "、".join(o.get("services", [])) or "—"
    activities = "、".join(o.get("activities", [])[:6]) or "—"
    return f"""
<div class="rec">
  <div class="rec-head">
    <span class="rec-rank">{idx}</span>
    <span class="rec-name">{o['name']}</span>
    <span class="rec-score">匹配度 {r['score']}</span>
  </div>
  <div class="rec-line"><span>👥</span><b>服务对象：</b><span>{o.get('target', '')}</span></div>
  <div class="rec-line"><span>🧰</span><b>能提供：</b><span>{services}</span></div>
  <div class="rec-line"><span>🎈</span><b>主要活动：</b><span>{activities}</span></div>
  <div class="rec-line"><span>💡</span><b>为什么推给你：</b><span>{badges}</span></div>
  <div class="rec-foot">
    ☎️ 联系方式：{o.get('contact') or '见机构公开渠道'}　｜　📅 更新：{o.get('updated', '')}<br>
    🔗 来源：<a href="{o.get('source_url', '')}" target="_blank">{o.get('source_name', '')}</a>
  </div>
</div>
"""


def render():
    _inject_style()
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
                f"来源：<a href="{p.get('source_url', '')}" target="_blank">{p.get('source_name', '')}</a></span>",
                unsafe_allow_html=True)

    st.divider()
    st.caption("想了解**怎么办理**（法律援助怎么申请、孩子入学要什么材料），切到「💬 智能问答」问一句，答案带官方来源。")
