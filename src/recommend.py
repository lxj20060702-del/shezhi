# -*- coding: utf-8 -*-
"""个性化推荐：按人群画像（性别 / 职业 / 是否有孩子 / 主要诉求）匹配公益组织与项目。

设计说明（对应《需求与任务大纲》功能模块②）：
- 画像 -> 关键词集合（带权重）
- 组织/项目的「名称+服务对象+服务+活动+标签」作为匹配语料
- 命中关键词累加权重，记录命中原因，按分数排序输出
- 全部未命中时走「通用兜底」推荐，保证页面永远有结果
"""
import kb

# ---- 画像选项 -> 匹配关键词（权重） ----
GENDER_KEYWORDS = {
    "女": {"流动女性": 3, "打工女性": 3, "女性": 2, "女工": 3, "打工妹": 3, "农村女性": 2, "打工妈妈": 2},
    "男": {"农民工": 2, "劳动者": 2, "打工者": 2, "新工人": 2},
}

JOB_KEYWORDS = {
    "家政 / 保洁": {"家政": 3, "打工女性": 2, "流动女性": 2, "打工妹": 2, "女性": 1},
    "餐饮 / 后厨": {"餐饮": 3, "服务业": 2, "打工者": 1, "女性": 1},
    "零售 / 商超 / 服务员": {"零售": 3, "服务业": 2, "打工者": 1},
    "工厂 / 制造业": {"制造业": 3, "工厂": 3, "女工": 2, "打工者": 1, "新工人": 1},
    "建筑 / 装修": {"建筑": 3, "农民工": 2, "劳动者": 1, "打工者": 1},
    "环卫 / 保洁外包": {"环卫": 3, "打工者": 1, "劳动者": 1},
    "做饭 / 送外卖 / 零工": {"服务业": 1, "打工者": 2, "流动人口": 1},
    "暂时没工作": {"打工者": 2, "流动人口": 1, "农民工": 1},
}

NEED_KEYWORDS = {
    "找活干 / 学一门技能": {"技能培训": 3, "培训": 2, "打工妹之家": 2, "文化教育": 1, "就业": 2},
    "被欠薪 / 劳动纠纷要维权": {"法律援助": 3, "权益维护": 3, "讨薪": 3, "劳动法": 2, "工伤": 3, "劳动纠纷": 3},
    "孩子上学 / 带娃": {"流动儿童": 3, "儿童": 2, "同心实验学校": 3, "子女": 2, "家庭": 1},
    "看病 / 身体健康": {"健康服务": 3, "紧急救援": 2, "医疗": 3},
    "想找人说说话 / 心理支持": {"同伴支持": 3, "社会工作": 2, "社区活动室": 2, "心理": 3},
    "想参加文艺活动 / 兴趣班": {"文艺活动": 3, "文化活动": 3, "艺术团": 3, "兴趣": 2, "演唱": 2, "瑜伽": 2,
                     "摄影": 2, "写作": 2, "书法": 2},
    "想找免费法律咨询": {"法律援助": 3, "劳动法": 3, "法律": 2},
    "住房 / 生活遇到困难": {"紧急救援": 3, "互惠": 2, "慈善": 2, "生活": 1},
}

CHILD_KEYWORDS = {"流动儿童": 3, "儿童": 2, "子女": 3, "家庭": 1, "同心实验学校": 3}

GENERIC_FALLBACK = ["org_xiezuozhe", "org_gongyou", "org_zhicheng"]

# 给界面用的选项列表
JOB_OPTIONS = list(JOB_KEYWORDS)
NEED_OPTIONS = list(NEED_KEYWORDS)


def _haystack(item):
    parts = [
        item.get("name", ""),
        " ".join(item.get("aliases", [])),
        item.get("target", ""),
        " ".join(item.get("services", [])),
        " ".join(item.get("activities", [])),
        " ".join(item.get("tags", [])),
        item.get("detail", ""),
        item.get("organizer", ""),
    ]
    return " ".join(p for p in parts if p)


def _build_weights(profile):
    """画像 -> {关键词: 权重}"""
    w = {}
    for kw, v in GENDER_KEYWORDS.get(profile.get("gender", ""), {}).items():
        w[kw] = w.get(kw, 0) + v
    for job in profile.get("jobs", []) or []:
        for kw, v in JOB_KEYWORDS.get(job, {}).items():
            w[kw] = w.get(kw, 0) + v
    for need in profile.get("needs", []) or []:
        for kw, v in NEED_KEYWORDS.get(need, {}).items():
            w[kw] = w.get(kw, 0) + round(v * 1.2)   # 诉求权重更高
    if profile.get("has_child"):
        for kw, v in CHILD_KEYWORDS.items():
            w[kw] = w.get(kw, 0) + v
    return w


def _score(item, weights):
    text = _haystack(item)
    score, hits = 0, []
    for kw, wt in weights.items():
        if kw and kw in text:
            score += wt
            hits.append(kw)
    return score, hits


def recommend(profile, top_n=5):
    """返回 {orgs:[{item,score,reasons}], programs:[...], weights, fallback:bool}"""
    orgs, programs = kb.get_orgs_and_programs()
    # 异地参照机构（如深圳绿色蔷薇）不参与「在京」推荐
    orgs = [o for o in orgs if "异地参照" not in o.get("type", "")]
    weights = _build_weights(profile)

    scored = []
    for o in orgs:
        s, hits = _score(o, weights)
        scored.append({"item": o, "kind": "组织", "score": s, "reasons": hits})
    scored.sort(key=lambda x: (-x["score"], x["item"].get("name", "")))

    fallback = all(x["score"] == 0 for x in scored)
    if fallback:
        order = {oid: i for i, oid in enumerate(GENERIC_FALLBACK)}
        picked = [x for x in scored if x["item"]["id"] in order]
        picked.sort(key=lambda x: order[x["item"]["id"]])
        for x in picked:
            x["reasons"] = ["通用推荐：面向外来务工者/流动人口的综合性服务"]
        scored = picked
    else:
        scored = [x for x in scored if x["score"] > 0]

    prog_scored = []
    for p in programs:
        s, hits = _score(p, weights)
        if s > 0:
            prog_scored.append({"item": p, "kind": "项目", "score": s, "reasons": hits})
    prog_scored.sort(key=lambda x: -x["score"])

    return {
        "orgs": scored[:top_n],
        "programs": prog_scored[:3],
        "weights": weights,
        "fallback": fallback,
    }


def summarize(profile, result):
    """生成一句人话总结，用于页面顶部展示。"""
    bits = []
    if profile.get("gender"):
        bits.append(profile["gender"] + "性")
    if profile.get("jobs"):
        bits.append("做" + "、".join(profile["jobs"]))
    if profile.get("has_child"):
        bits.append("有孩子")
    who = "、".join(bits) if bits else "在京务工的朋友"
    n = len(result["orgs"])
    if result["fallback"]:
        return f"按「{who}」为你准备了 {n} 家综合性的公益组织，都能提供基础服务与转介。"
    needs = profile.get("needs") or []
    what = "、".join(needs) if needs else "你的需求"
    return f"按「{who}」+ 想解决「{what}」，共匹配到 {n} 家可以帮上忙的机构。"
