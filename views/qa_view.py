# -*- coding: utf-8 -*-
"""💬 智能问答页

- 🎨 页面设计：改这里的布局、文案、按钮样式（配合 assets/style.css）
- ⚙️ 功能实现：问答逻辑在 src/qa.py（检索 src/retriever.py、大模型 src/llm.py）
"""
import streamlit as st

EXAMPLES = [
    "外地务工人员在北京怎么申请免费法律援助？",
    "孩子在京上学需要什么材料？",
    "有哪些服务流动女性的公益组织？办过什么文艺活动？",
]


def render(qa):
    st.markdown('<p class="qa-hint">💭 不知道从哪问起？试试下面这些问题，或者直接写下你的困惑～</p>',
                unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLES))
    example = None
    for col, text in zip(cols, EXAMPLES):
        if col.button(text, use_container_width=True):
            example = text

    st.markdown('<p class="qa-ask">✍️ 在这里提问</p>', unsafe_allow_html=True)
    q = st.chat_input("说说你想了解什么～她知帮你找答案 🌸")
    if example:
        q = example

    if not q:
        return

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
