# -*- coding: utf-8 -*-
"""知识库加载：把 orgs / policies 打平成可检索文档。"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(fn):
    with open(DATA_DIR / fn, encoding="utf-8") as f:
        return json.load(f)


def load_documents():
    """返回文档列表，每篇含 id/type/title/text/来源等字段。"""
    docs = []

    orgs = _load("organizations.json")
    for o in orgs.get("organizations", []):
        text = " ".join([
            o["name"], " ".join(o.get("aliases", [])),
            f"服务对象：{o.get('target','')}",
            "服务内容：" + "、".join(o.get("services", [])),
            "活动：" + "、".join(o.get("activities", [])),
            f"成立：{o.get('founded','')}",
            "标签：" + "、".join(o.get("tags", [])),
        ])
        docs.append({
            "id": o["id"], "type": "组织", "title": o["name"],
            "text": text, "tags": o.get("tags", []),
            "source_name": o.get("source_name", ""), "source_url": o.get("source_url", ""),
            "updated": o.get("updated", ""), "raw": o,
        })

    for p in orgs.get("programs", []):
        text = f"{p['name']} 主办：{p.get('organizer','')} 时间：{p.get('since','')} {p.get('detail','')}"
        docs.append({
            "id": p["id"], "type": "项目", "title": p["name"], "text": text,
            "tags": p.get("tags", []), "source_name": p.get("source_name", ""),
            "source_url": p.get("source_url", ""), "updated": p.get("updated", ""), "raw": p,
        })

    pol = _load("policies.json")
    for p in pol.get("policies", []):
        text = " ".join([
            p["title"], f"主题：{p.get('topic','')}",
            p.get("summary", ""),
            "办理步骤：" + "；".join(p.get("steps", [])),
            "所需材料：" + "、".join(p.get("materials", [])),
            "办理渠道：" + "、".join(p.get("channels", [])),
            "发布机构：" + p.get("publisher", ""),
        ])
        docs.append({
            "id": p["id"], "type": "政策", "title": p["title"], "text": text,
            "tags": p.get("tags", []), "source_name": p.get("source_name", ""),
            "source_url": p.get("source_url", ""), "updated": p.get("updated", ""), "raw": p,
        })

    return docs


def get_orgs_and_programs():
    orgs = _load("organizations.json")
    return orgs.get("organizations", []), orgs.get("programs", [])


def get_policies():
    return _load("policies.json").get("policies", [])
