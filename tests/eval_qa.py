# -*- coding: utf-8 -*-
"""功能A · 问答准确率评测脚本（T9）

评测两层：
  1) 路由准确率：政策问题是否进入政策库、组织问题是否进入组织库
  2) 检索命中率：topk 检索结果里是否包含期望条目（即答案有正确依据）

运行：
  pip install jieba streamlit
  python eval_qa.py
说明：不调用大模型、不消耗 API，只测检索链路；大模型答案质量需人工按
data/测试问题集.md 的“验收要点”逐条核对。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import kb  # noqa: E402
from retriever import BM25Retriever  # noqa: E402
from qa import _is_policy  # noqa: E402

# (问题, 期望路由类型, 期望命中的政策/组织 id)
CASES = [
    # 政策类 6 题
    ("外地务工人员在北京怎么申请免费法律援助？", "政策", "pol_legal_aid"),
    ("孩子在京上学需要什么材料？", "政策", "pol_school"),
    ("老板拖欠工资不给怎么办？", "政策", "pol_wage_arrears"),
    ("我在工地上受伤了，怎么申请工伤认定？", "政策", "pol_work_injury"),
    ("北京市居住证怎么办，需要什么条件？", "政策", "pol_residence"),
    ("北京医保怎么报销、去哪个官方网站查？", "政策", "pol_medical_insurance"),
    # 组织类 4 题
    ("有哪些服务流动女性的公益组织？办过什么文艺活动？", "组织", "org_mulan"),
    ("打工姐妹想参加文艺演出，哪家机构有这样的活动？", "组织", "org_mulan"),
    ("被公司辞退、需要劳动法律咨询，可以找哪家机构？", "组织", "org_yilian"),
    ("北京哪里能找到给农民工做法律援助的机构？", "组织", "org_zhicheng"),
]


def main():
    retriever = BM25Retriever(docs=kb.load_documents())
    id_index = {d["id"]: d for d in retriever.docs}

    route_ok = 0
    retrieval_ok = 0
    rows = []

    for q, want_route, want_id in CASES:
        got_route = "政策" if _is_policy(q) else "组织"
        route_pass = got_route == want_route

        # 按期望路由检索，看 top4 是否命中目标条目
        docs = retriever.search(q, doc_type=want_route, topk=4)
        if not docs:  # 与线上一致的兜底：跨类型再检一次
            docs = retriever.search(q, topk=4)
        hit_ids = [d["id"] for d in docs]
        hit_pass = want_id in hit_ids

        route_ok += route_pass
        retrieval_ok += hit_pass
        rows.append((q, want_route, got_route, "✅" if route_pass else "❌",
                    "✅" if hit_pass else "❌",
                    id_index.get(want_id, {}).get("title", want_id)))

    n = len(CASES)
    print("=" * 78)
    print(f"{'问题':<32}{期望:^6}{实际:^6}{路由:^5}{检索:^5} 依据条目")
    print("-" * 78)
    for q, wr, gr, rp, hp, title in rows:
        print(f"{q[:30]:<32}{wr:^6}{gr:^6}{rp:^5}{hp:^5} {title[:24]}")
    print("=" * 78)
    print(f"路由准确率：{route_ok}/{n} = {route_ok/n:.0%}")
    print(f"检索命中率：{retrieval_ok}/{n} = {retrieval_ok/n:.0%}")

    result = {
        "total": n,
        "route_accuracy": round(route_ok / n, 4),
        "retrieval_hit_rate": round(retrieval_ok / n, 4),
        "cases": [
            {"question": q, "want_route": wr, "got_route": gr,
             "route_pass": rp == "✅", "retrieval_pass": hp == "✅"}
            for q, wr, gr, rp, hp, _ in rows
        ],
    }
    out = ROOT / "tests" / "eval_result.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("结果已保存：", out)


if __name__ == "__main__":
    main()
