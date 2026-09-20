# -*- coding: utf-8 -*-
"""RAG 问答：检索 -> 组装证据 -> 大模型生成（带来源标注）-> 降级兜底。"""
import re

from retriever import BM25Retriever
from llm import LLM

POLICY_HINT = ["政策", "法律援助", "入学", "社保", "居住证", "维权", "怎么", "如何", "材料", "申请", "办理", "需要"]
ORG_HINT = ["组织", "机构", "活动", "文艺", "参加", "联系", "有哪些", "往年"]

SYSTEM_PROMPT = (
    "你是“她知”，面向北京流动女性的公益知识助手。"
    "请严格依据【参考资料】回答，不要编造；若资料不足，请明确说明“资料中暂未收录”。"
    "用通俗、口语化、友善的中文回答，分点、简短。"
    "每条关键信息后用【来源N】标注依据。政策类必须与官方口径一致。"
)


def _is_policy(q):
    return sum(h in q for h in POLICY_HINT) >= sum(h in q for h in ORG_HINT)


class QA:
    def __init__(self):
        self.retriever = BM25Retriever()
        self.llm = LLM()

    def _route(self, q):
        """政策类走政策库，组织类走组织库。"""
        return "政策" if _is_policy(q) else "组织"

    def answer(self, q, topk=4):
        route = self._route(q)
        docs = self.retriever.search(q, doc_type=route, topk=topk)
        if not docs:
            docs = self.retriever.search(q, topk=topk)

        context = "\n\n".join(
            f"【来源{i+1}】{d['title']}（{d['type']}｜来源：{d['source_name']} {d['source_url']}）\n{d['text']}"
            for i, d in enumerate(docs)
        )
        user = f"【参考资料】\n{context}\n\n【用户问题】{q}\n\n请依据资料作答并标注【来源N】。"

        text = self.llm.chat(SYSTEM_PROMPT, user)
        if text and not text.startswith("[大模型调用失败"):
            return {"route": route, "mode": "RAG+大模型", "answer": text, "sources": docs}

        # 降级：无大模型时，输出“可核验”的检索式答案
        fallback = self._extractive(docs, q)
        return {"route": route, "mode": "检索式（未配置大模型）", "answer": fallback, "sources": docs}

    @staticmethod
    def _extractive(docs, q):
        lines = [f"根据知识库检索到的权威信息（问题：{q}）：", ""]
        for i, d in enumerate(docs):
            lines.append(f"【来源{i+1}】{d['title']}")
            raw = d["raw"]
            if d["type"] == "政策":
                if raw.get("summary"):
                    lines.append("· " + raw["summary"])
                for s in raw.get("steps", [])[:4]:
                    lines.append("· " + s)
                if raw.get("materials"):
                    lines.append("· 所需材料：" + "、".join(raw["materials"]))
                if raw.get("caveat"):
                    lines.append("⚠️ " + raw["caveat"])
            else:
                lines.append("· 服务对象：" + str(raw.get("target", "")))
                if raw.get("services"):
                    lines.append("· 服务内容：" + "、".join(raw["services"]))
                if raw.get("activities"):
                    lines.append("· 相关活动：" + "、".join(raw["activities"]))
            lines.append(f"· 来源：{d['source_name']} {d['source_url']}（更新 {d['updated']}）")
            lines.append("")
        lines.append("（配置免费大模型 API Key 后，将自动切换为大模型生成式回答）")
        return "\n".join(lines)


if __name__ == "__main__":
    qa = QA()
    for q in ["外地务工人员在北京怎么申请免费法律援助？",
              "孩子在京上学需要什么材料？",
              "北京有哪些服务流动女性的公益组织？往年办过哪些文艺活动？"]:
        r = qa.answer(q)
        print("=" * 60)
        print("Q:", q, "| 路由:", r["route"], "| 模式:", r["mode"])
        print(r["answer"][:600])
