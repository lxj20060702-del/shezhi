# -*- coding: utf-8 -*-
"""📚 知识库页（组织库 / 政策库表格）

- 🎨 页面设计：改列名、列宽、展示字段（表格列定义在 ORG_COLS / POL_COLS 的字典里）
- ⚙️ 功能实现：数据在 data/organizations.json、data/policies.json；字段说明见 docs/数据源核实清单.md
"""
import streamlit as st


def render(orgs, policies):
    st.subheader("公益组织库")
    st.dataframe(
        [{"名称": o["name"], "服务对象": o.get("target", ""),
          "核心服务/活动": "、".join(o.get("services", []) + o.get("activities", []))[:60],
          "来源": o.get("source_name", "")} for o in orgs],
        use_container_width=True)

    st.subheader("政策知识库")
    st.dataframe(
        [{"主题": p.get("topic", ""), "标题": p.get("title", ""),
          "发布机构": p.get("publisher", ""),
          "生效/更新": p.get("effective_date", "") or p.get("updated", "")} for p in policies],
        use_container_width=True)

    st.caption("数据均为公开信息，逐条核实；引用需注明出处（详见 docs/数据源核实清单.md）。")
