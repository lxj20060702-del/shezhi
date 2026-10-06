# -*- coding: utf-8 -*-
"""RAG 问答：检索 -> 组装证据 -> 大模型生成 -> 来源独立展示 -> 降级兜底。"""
import re

from retriever import BM25Retriever
from llm import LLM

# 路由关键词（v0.3：补齐欠薪/工伤/医保等高频词，降低误路由率）
POLICY_HINT = [
    "政策", "法律援助", "入学", "上学", "社保", "医保", "保险", "居住证", "维权",
    "怎么", "如何", "材料", "申请", "办理", "需要", "欠薪", "讨薪", "拖欠", "工资",
    "工伤", "养老", "失业", "退休", "报销", "纳税", "12333", "12348", "补贴",
    "家暴", "家庭暴力", "反家暴", "产假", "生育", "哺乳", "怀孕", "最低工资",
    "公租房", "租房", "公积金", "住房公积金", "低保", "救助", "困难", "培训",
    "技能", "创业", "两癌", "筛查", "孕产妇", "母婴", "中考", "职业学校",
    "性骚扰", "歧视", "妇女权益", "离婚", "育儿", "异地就医", "跨省", "备案",
    "12338", "12345", "12329", "就业", "岗位",
]
ORG_HINT = [
    "组织", "机构", "活动", "文艺", "参加", "联系", "有哪些", "往年", "社团",
    "中心", "哪里有", "哪家", "找到", "找谁", "哪里能",
    "家政", "鸿雁", "同心", "打工妹", "木兰", "协作者", "工友之家",
    "爱心超市", "合唱团", "互助", "姐妹", "志愿者",
    # 公益项目/计划触发词（与政策类“创业/培训”区分：这些是可参加的公益项目）
    "项目", "公益项目", "春蕾", "母亲健康快车", "他乡的你", "巾帼贷款",
    "贷款项目", "助学", "捐赠", "帮扶计划",
]

# 项目强锚点：只要命中具体公益项目名，无论句子里是否带“怎么/申请”等功能词，
# 一律走资源侧，避免被政策功能词错误拽回政策库。
PROJECT_ANCHORS = [
    "春蕾", "母亲健康快车", "他乡的你", "家庭成长计划",
    "巾帼贷款", "妇女创业担保贷款", "金融支持妇女", "农村妇女创新创业",
]

# 弱命中阈值：top1 原始 BM25 分低于此值，视为知识库无高度相关内容（实测标定）。
WEAK_SCORE = 6.0

_GREETINGS = {
    "你好", "您好", "hi", "hello", "哈喽", "嗨", "在吗", "在么", "早",
    "早上好", "晚上好", "谢谢", "感谢", "再见", "拜拜", "你是谁", "你叫什么",
}

GUIDE_REPLY = "\n".join([
    "你好呀，我是“她知”，专注为在北京生活的流动女性解答政策与公益服务问题。",
    "你可以这样问我，例如：",
    "· 老板拖欠工资怎么办",
    "· 我被老公打了，怎么保护自己",
    "· 孩子在北京上学需要什么材料",
    "· 北京有哪些帮助流动女性的公益组织",
    "遇到紧急危险，请直接拨打 12338 妇女维权热线或 110 报警。",
])

WEAK_REPLY = "\n".join([
    "抱歉，关于这个问题，我的知识库里暂时没有找到高度相关的权威信息，为了不给你错误的建议，我不做猜测。你可以：",
    "· 拨打 12345 市民服务热线咨询各类生活与政务问题；",
    "· 涉及妇女权益可拨打 12338 妇女维权公益服务热线；",
    "· 换个更具体的说法再问我一次。",
    "下方是相关性较弱的资料，仅供参考。",
])


def _is_meaningless(q):
    """识别空输入、纯数字/标点、过短无中文、寒暄等无检索意义的内容。"""
    if not q:
        return True
    if q.lower() in _GREETINGS:
        return True
    has_cjk = bool(re.search(r"[一-鿿]", q))
    if not has_cjk and len(q) < 6:
        return True
    if not re.search(r"[一-鿿a-zA-Z]", q):
        return True
    return False


SYSTEM_PROMPT = (
    "你是“她知”，面向北京流动女性的公益知识助手。"
    "请严格依据【参考资料】回答，不要编造。"
    "回答使用自然语言，不使用任何引用格式。"
    "禁止输出以下内容："
    "【来源1】、【来源2】、[来源1]、(来源1)。"
    "不要解释来源，不要生成参考文献列表。"
    "来源由系统页面单独展示。"
    "回答简洁、友善、分点。"
    "如果用户问题与北京流动女性权益、政策、公益服务无关，"
    "请告知用户本系统专注于北京流动女性相关政策咨询，"
    "建议通过12345市民服务热线获取其他帮助。"
)


def _is_policy(q):
    # 明确提到具体公益项目名 → 资源侧（优先级最高）
    if any(a in q for a in PROJECT_ANCHORS):
        return False
    return sum(h in q for h in POLICY_HINT) >= sum(h in q for h in ORG_HINT)


class QA:
    def __init__(self):
        self.retriever = BM25Retriever()
        self.llm = LLM()

    def _route(self, q):
        """政策类走政策库；资源类同时检索公益组织与公益项目。"""
        return "政策" if _is_policy(q) else "资源"

    def answer(self, q, topk=4):
        q = (q or "").strip()

        # ① 无意义/寒暄输入：给出使用引导，不检索、不调用大模型
        if _is_meaningless(q):
            return {"route": "寒暄", "mode": "使用引导", "answer": GUIDE_REPLY, "sources": []}

        route = self._route(q)
        if route == "政策":
            doc_type = ("政策",)
        else:
            doc_type = ("组织", "项目")  # 组织与公益项目同属“社会资源”，一并打分
        scored = self.retriever.search_with_scores(q, doc_type=doc_type, topk=topk)
        if not scored:
            scored = self.retriever.search_with_scores(q, topk=topk)
        docs = [d for d, _ in scored]

        # ② 弱命中：top1 分数过低说明无高度相关内容，诚实兜底而非硬答
        top1 = scored[0][1] if scored else 0.0
        if top1 < WEAK_SCORE:
            return {"route": route, "mode": "弱命中兜底", "answer": WEAK_REPLY, "sources": docs}

        context = "\n\n".join(
    f"【资料{i+1}】：{d['title']}（{d['type']}｜来源：{d['source_name']} {d['source_url']}）\n{d['text']}"
    for i, d in enumerate(docs)
        )
        user = f"""
        【参考资料】

        {context}

        【用户问题】

        {q}

        请严格依据参考资料回答。
        只输出给用户看的正文。
        不要输出资料编号。
        不要输出【来源1】、【来源2】等格式。
        来源信息由系统单独展示。
        """

        text = self.llm.chat(SYSTEM_PROMPT, user)

        # 清理大模型生成的引用标记
        if text:
            text = re.sub(r'【来源\s*\d+】', '', text)
            text = re.sub(r'\[来源\s*\d+\]', '', text)
            text = re.sub(r'来源\s*\d+', '', text)
            text = re.sub(r'\(来源\s*\d+\)', '', text)
            text = re.sub(r'（来源\s*\d+）', '', text)

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
            elif d["type"] == "项目":
                if raw.get("organizer"):
                    lines.append("· 主办单位：" + str(raw["organizer"]))
                if raw.get("since"):
                    lines.append("· 启动时间：" + str(raw["since"]))
                if raw.get("detail"):
                    lines.append("· 项目介绍：" + str(raw["detail"]))
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
