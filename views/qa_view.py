# -*- coding: utf-8 -*-
"""💬 智能问答页

- 🎨 页面设计：改这里的布局、文案、按钮样式（配合 assets/style.css）
- ⚙️ 功能实现：问答逻辑在 src/qa.py（检索 src/retriever.py、大模型 src/llm.py）

v0.6（功能A多轮引导配套）：新增历史消息重绘与“清空对话”，未改动原有样式与布局。
"""
import streamlit as st

EXAMPLES = [
    "外地务工人员在北京怎么申请免费法律援助？",
    "孩子在京上学需要什么材料？",
    "有哪些服务流动女性的公益组织？办过什么文艺活动？",
]


def _render_sources(sources):
    """渲染“查看依据”折叠区。"""
    if not sources:
        return
    with st.expander("🔍 查看依据（可溯源）"):
        for i, d in enumerate(sources):
            st.markdown(
                f'<div class="src"><b>【来源{i+1}】{d["title"]}</b>　'
                f'<span style="color:#888">{d["type"]}</span><br>'
                f'{d["source_name"]} · <a href="{d["source_url"]}" target="_blank">{d["source_url"]}</a><br>'
                f'<span style="color:#888">更新：{d["updated"]}</span></div>',
                unsafe_allow_html=True)


def render(qa):
    st.markdown('<p class="qa-hint">💭 不知道从哪问起？试试下面这些问题，或者直接写下你的困惑～</p>',
                unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLES))
    example = None
    for col, text in zip(cols, EXAMPLES):
        if col.button(text, use_container_width=True):
            example = text

    # 多轮历史：展示用消息列表（含每轮依据），与 qa 内部会话状态同步
    if "qa_messages" not in st.session_state:
        st.session_state["qa_messages"] = []
    messages = st.session_state["qa_messages"]

    top_cols = st.columns([1, 1, 1, 1])
    with top_cols[-1]:
        if messages and st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state["qa_messages"] = []
            qa.reset()
            st.rerun()

    # 先重绘历史消息，保证多轮对话完整可见
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=False)
            if msg["role"] == "assistant":
                _render_sources(msg.get("sources", []))

    st.markdown('<p class="qa-ask">✍️ 在这里提问</p>', unsafe_allow_html=True)
    q = st.chat_input("说说你想了解什么～她知帮你找答案 🌸")
    if example:
        q = example

    if not q:
        return

    with st.chat_message("user"):
        st.write(q)
    messages.append({"role": "user", "content": q})

    with st.chat_message("assistant"):
        with st.spinner("检索知识库中…"):
            res = qa.answer(q)
        answer = res["answer"]

        # 把正文里的【来源1】替换成链接
        for i, d in enumerate(res["sources"]):
            url = d["source_url"]
            answer = answer.replace(
                f"【来源{i+1}】",
                f"[【来源{i+1}】]({url})"
            )

        st.markdown(answer, unsafe_allow_html=False)

        st.caption(f"路由：{res['route']}库 · 模式：{res['mode']}")
        _render_sources(res["sources"])

    messages.append({
        "role": "assistant", "content": answer, "sources": res["sources"],
    })
