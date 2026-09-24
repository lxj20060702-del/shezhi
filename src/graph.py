# -*- coding: utf-8 -*-
"""轻量公益服务知识图谱：实体=组织/项目/政策/服务/人群标签，关系=服务/举办/适用/发布。"""
import json

import kb


def build_graph():
    nodes, edges = [], []
    seen = set()

    def add(nid, label, ntype):
        if nid not in seen:
            seen.add(nid)
            nodes.append({"id": nid, "label": label, "type": ntype})

    orgs, programs = kb.get_orgs_and_programs()
    for o in orgs:
        add(o["id"], o["name"], "组织")
        for tag in o.get("tags", []):
            tid = "tag_" + tag
            add(tid, tag, "人群标签")
            edges.append({"from": o["id"], "to": tid, "label": "面向"})
        for s in o.get("services", []):
            sid = "srv_" + s
            add(sid, s, "服务")
            edges.append({"from": o["id"], "to": sid, "label": "提供"})

    for p in programs:
        add(p["id"], p["name"], "项目")
        for tag in p.get("tags", []):
            tid = "tag_" + tag
            add(tid, tag, "人群标签")
            edges.append({"from": p["id"], "to": tid, "label": "面向"})

    for p in kb.get_policies():
        add(p["id"], p["title"], "政策")
        for tag in p.get("tags", []):
            tid = "tag_" + tag
            add(tid, tag, "人群标签")
            edges.append({"from": p["id"], "to": tid, "label": "适用"})

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    g = build_graph()
    print(json.dumps({"nodes": len(g["nodes"]), "edges": len(g["edges"])},
                     ensure_ascii=False))
