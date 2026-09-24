# -*- coding: utf-8 -*-
"""🎯 为你推荐页（功能模块②：组织与活动个性化推荐）

- 🎨 页面设计：卡片样式与手机端适配在 _inject_style；卡片 HTML 在 _card_html
- ⚙️ 功能实现：匹配算法在 src/recommend.py；数据在 data/organizations.json
"""
import streamlit as st

from recommend import recommend, summarize, JOB_OPTIONS, NEED_OPTIONS


def _inject_style():
    """推荐页专属样式：棕色为主 + 粉色点缀 + 手机端适配。"""
    st.markdown("""
<style>
/* ---------- 配色变量 ---------- */
:root {
  --brown: #8B5E3C;
  --brown-dark: #5C3D2E;
  --brown-soft: #F7F0E8;
  --brown-line: #E8DDD0;
  --pink: #E8879B;
  --pink-soft: #FDF0F3;
  --sakura: #F2A6B8;  /* 樱花粉（表单选中色） */
  --cream: #F5EFE6;   /* 米白色（multiselect 标签底） */
}

/* ---------- 表单组件配色覆盖（仅本页） ---------- */
/* radio 选中圆标 → 樱花粉（仅作用于推荐页的 radiogroup） */
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child,
div[role="radiogroup"] label > div:first-child {
  background-color: var(--sakura) !important;
  border-color: var(--sakura) !important;
}
div[role="radiogroup"] input[type="radio"] {
  accent-color: var(--sakura) !important;
}

/* multiselect 已选标签 → 米白底 + 深棕字 */
div.stMultiSelect [data-baseweb="tag"],
div.stMultiSelect [role="group"] > span {
  background: var(--cream) !important;
  border: 1px solid var(--brown-line) !important;
  border-radius: 6px !important;
}
div.stMultiSelect [data-baseweb="tag"] span,
div.stMultiSelect [role="group"] > span span {
  color: var(--brown-dark) !important;
  font-size: .85rem;
}
div.stMultiSelect [data-baseweb="tag"] [data-baseweb="tag-close-icon"],
div.stMultiSelect [role="group"] > span [aria-label*="remove"] {
  color: var(--brown-dark) !important;
}
div.stMultiSelect [data-baseweb="tag"] svg,
div.stMultiSelect [role="group"] svg {
  fill: var(--brown-dark) !important;
  stroke: var(--brown-dark) !important;
}
/* multiselect 下拉面板选中项 */
div.stMultiSelect [data-baseweb="menu"] [role="option"][aria-selected="true"],
div.stMultiSelect ul[role="listbox"] li[aria-selected="true"] {
  background: var(--brown-soft) !important;
  color: var(--brown-dark) !important;
}

/* 提交按钮 → 棕色主色 */
button[data-testid="stBaseButton-secondaryFormSubmit"],
.stButton > button,
button[kind="secondaryFormSubmit"] {
  background: var(--brown) !important;
  border: 1px solid var(--brown) !important;
  color: #fff !important;
  border-radius: 10px !important;
  transition: background .2s ease;
}
button[data-testid="stBaseButton-secondaryFormSubmit"]:hover,
.stButton > button:hover,
button[kind="secondaryFormSubmit"]:hover {
  background: var(--brown-dark) !important;
  border-color: var(--brown-dark) !important;
}

/* ---------- 推荐卡片 ---------- */
.rec {
  position: relative;
  border: 1px solid var(--brown-line);
  border-radius: 16px;
  padding: 18px 20px 18px 24px;
  margin: 14px 0;
  background: #fff;
  box-shadow: 0 2px 8px rgba(139,94,60,.06), 0 1px 3px rgba(0,0,0,.03);
  transition: box-shadow .25s ease, transform .25s ease, border-color .25s ease;
  overflow: hidden;
}
/* 左侧棕色装饰条 */
.rec::before {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 5px;
  background: linear-gradient(180deg, var(--brown) 0%, var(--pink) 100%);
  border-radius: 16px 0 0 16px;
}
.rec:hover {
  box-shadow: 0 8px 24px rgba(139,94,60,.16);
  transform: translateY(-2px);
  border-color: var(--brown);
}

/* ---------- 卡片头部 ---------- */
.rec-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.rec-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--brown);
  color: #fff;
  font-size: .85rem;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(139,94,60,.3);
}
.rec-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--brown-dark);
  flex: 1;
  min-width: 0;
}
.rec-score {
  background: var(--pink-soft);
  color: #C25A72;
  border: 1px solid #F5D5DD;
  border-radius: 999px;
  padding: 3px 12px;
  font-size: .8rem;
  font-weight: 600;
  white-space: nowrap;
}

/* ---------- 信息行 ---------- */
.rec-line {
  font-size: .9rem;
  color: #444;
  margin: 6px 0;
  line-height: 1.65;
  display: flex;
  gap: 6px;
  align-items: flex-start;
}
.rec-line b {
  color: var(--brown);
  font-weight: 600;
  flex-shrink: 0;
}
/* 标签：粉色底 + 深棕字，适配棕色主题并增加点缀 */
.rec-line code {
  background: var(--pink-soft);
  color: var(--brown-dark);
  border: 1px solid #F5D5DD;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: .78rem;
  font-weight: 500;
  margin: 1px 2px;
  display: inline-block;
}

/* ---------- "为什么推给你"区块 ---------- */
.rec-reason {
  background: var(--brown-soft);
  border: 1px solid var(--brown-line);
  border-radius: 10px;
  padding: 10px 14px;
  margin: 10px 0 4px;
}

/* ---------- 分隔线 ---------- */
.rec-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--brown-line), transparent);
  margin: 12px 0;
}

/* ---------- 推荐统计区块 ---------- */
.rec-stats {
  display: flex;
  gap: 12px;
  margin: 0 0 16px;
  flex-wrap: wrap;
}
.rec-stat-card {
  flex: 1;
  min-width: 120px;
  background: #fff;
  border: 1px solid var(--brown-line);
  border-radius: 12px;
  padding: 12px 16px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(139,94,60,.05);
}
.rec-stat-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--brown);
  line-height: 1.2;
}
.rec-stat-label {
  font-size: .78rem;
  color: #8B7355;
  margin-top: 2px;
}
.rec-stat-card:nth-child(2) .rec-stat-num { color: var(--pink); }

/* ---------- 底部信息 ---------- */
.rec-foot {
  margin-top: 4px;
  padding-top: 10px;
  border-top: 1px dashed var(--brown-line);
  font-size: .83rem;
  color: #8B7355;
  line-height: 1.7;
}
.rec-foot a {
  color: var(--pink);
  text-decoration: none;
  font-weight: 600;
}
.rec-foot a:hover {
  text-decoration: underline;
  color: #C25A72;
}

/* ---------- 推荐结果摘要区块 ---------- */
.rec-summary {
  background: linear-gradient(135deg, var(--brown-soft) 0%, var(--pink-soft) 100%);
  border: 1px solid var(--brown-line);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 10px 0 18px;
  font-size: .92rem;
  color: var(--brown-dark);
  line-height: 1.7;
}
.rec-summary b {
  color: var(--brown);
}

/* ---------- 手机端（≤640px） ---------- */
@media (max-width: 640px) {
  .rec { padding: 14px 16px 14px 20px; margin: 10px 0; border-radius: 14px; }
  .rec-name { font-size: 1rem; }
  .rec-line { font-size: .86rem; margin: 5px 0; }
  .rec-line code { font-size: .72rem; padding: 2px 8px; }
  .rec-score { font-size: .74rem; padding: 2px 9px; }
  .rec-rank { min-width: 26px; height: 26px; font-size: .76rem; }
  .rec-foot { font-size: .78rem; }
  .rec-summary { padding: 12px 14px; font-size: .86rem; }
  .rec-reason { padding: 8px 10px; }
  .rec-stats { gap: 8px; }
  .rec-stat-card { padding: 10px 8px; min-width: 90px; }
  .rec-stat-num { font-size: 1.2rem; }
  .rec-stat-label { font-size: .72rem; }
}
</style>""", unsafe_allow_html=True)


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
  <div class="rec-reason">
    <div class="rec-line"><span>💡</span><b>为什么推给你：</b><span>{badges}</span></div>
  </div>
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
    st.markdown(f'<div class="rec-summary"><b>🎯 推荐结果</b>：{summarize(profile, res)}</div>', unsafe_allow_html=True)

    # 推荐统计区块
    org_count = len(res["orgs"])
    max_score = max((r["score"] for r in res["orgs"]), default=0)
    st.markdown(f"""
<div class="rec-stats">
  <div class="rec-stat-card">
    <div class="rec-stat-num">{org_count}</div>
    <div class="rec-stat-label">匹配机构数</div>
  </div>
  <div class="rec-stat-card">
    <div class="rec-stat-num">{max_score}</div>
    <div class="rec-stat-label">最高匹配度</div>
  </div>
  <div class="rec-stat-card">
    <div class="rec-stat-num">{len(res["programs"])}</div>
    <div class="rec-stat-label">相关项目</div>
  </div>
</div>
""", unsafe_allow_html=True)

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
