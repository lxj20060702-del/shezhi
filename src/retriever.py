# -*- coding: utf-8 -*-
"""轻量检索：jieba 分词 + BM25，本地零依赖、零成本。

v0.4 质量增强：
- 停用词过滤：剔除虚词/功能词，避免“了/被/怎么”成为打分主力；
- 查询同义词扩展：把用户口语（老公/上班/打）映射到知识库书面语（配偶/就业/家暴）；
- search_with_scores：返回原始分数，供上层判断“弱命中”做诚实兜底。
"""
import math
import re
from collections import Counter

import jieba

import kb

# 停用词：仅收录高频虚词/疑问功能词，不收录“政策/申请”等可能有检索意义的词。
# 注意：路由（qa.POLICY_HINT）在停用词过滤之前进行，这里过滤不影响路由判断。
STOPWORDS = {
    "的", "了", "在", "是", "我", "你", "他", "她", "们", "吗", "呢", "吧", "啊",
    "被", "把", "给", "和", "与", "及", "或", "也", "都", "就", "又", "还", "很",
    "最", "不", "没", "有", "个", "这", "那", "些", "之", "其", "着", "过", "地",
    "得", "以", "于", "向", "对", "为", "让", "使", "能", "会", "要", "想", "可",
    "什么", "怎么", "怎样", "如何", "为什么", "哪里", "哪儿", "哪个", "请问",
    "一下", "现在", "已经", "可以", "应该", "需要",
}

# 口语 → 知识库书面语（token 级，作用于查询分词结果）
SYNONYMS = {
    "老公": ["配偶", "丈夫", "家庭暴力", "家暴"],
    "上班": ["就业", "岗位", "工作"],
    "打工": ["务工", "就业", "工作"],
    "打工妹": ["流动女性", "务工妇女", "女职工"],
    "媳妇": ["配偶", "妇女"],
    "老婆": ["配偶", "妻子"],
    "生孩子": ["生育", "分娩", "产假"],
    "怀孕": ["妊娠", "孕期"],
    "讨薪": ["欠薪", "拖欠工资", "工资"],
    "要工资": ["欠薪", "拖欠工资"],
    "妇联": ["妇女联合会", "12338"],
    "妇女组织": ["妇女联合会", "公益组织", "12338"],
    "租房子": ["租房", "住房"],
    "上学": ["入学", "就读"],
    "找个班上": ["就业", "岗位", "找工作", "求职"],
    "找班上": ["就业", "岗位", "找工作", "求职"],
    "找工作": ["就业", "岗位", "求职", "就业援助"],
    "干活": ["务工", "工作", "就业"],
    "没活": ["失业", "就业援助", "就业", "岗位"],
    "咋": ["如何", "怎么"],
    "咋办": ["怎么办", "如何处理"],
    "咋整": ["怎么办"],
}

# 短语模式：需结合上下文才追加的词，避免单字“打”误伤（打车/打架）
PHRASE_PATTERNS = [
    (re.compile(r"(老公|丈夫|配偶|男朋友|对象).{0,3}打|打.{0,3}(老公|丈夫|他|我|媳妇|老婆|架)"),
     ["家庭暴力", "家暴", "人身安全保护令", "妇联"]),
    (re.compile(r"老板.{0,4}(不给|拖欠|克扣|不发).{0,2}(工资|钱)|(工资|工钱).{0,3}(不给|拖欠)"),
     ["欠薪", "拖欠工资", "劳动监察"]),
]


def _expand_query(q):
    """把口语查询扩展为书面语词列表（原始 token + 追加同义词）。"""
    extra = []
    for pat, words in PHRASE_PATTERNS:
        if pat.search(q):
            extra.extend(words)
    for colloquial, formal in SYNONYMS.items():
        if colloquial in q:
            extra.extend(formal)
    return extra


class BM25Retriever:
    def __init__(self, docs=None, k1=1.5, b=0.75):
        self.docs = docs or kb.load_documents()
        self.k1, self.b = k1, b
        self.corpus_tokens = [self._tok(d["text"] + " " + d["title"]) for d in self.docs]
        self.doc_len = [len(t) for t in self.corpus_tokens]
        self.avgdl = sum(self.doc_len) / max(len(self.doc_len), 1)
        self.df = Counter()
        for toks in self.corpus_tokens:
            for w in set(toks):
                self.df[w] += 1
        self.N = len(self.docs)

    def _tok(self, s):
        return [w for w in jieba.lcut_for_search(s) if w.strip() and w not in STOPWORDS]

    def _query_tokens(self, query):
        """查询分词：停用词过滤 + 口语同义词扩展。"""
        tokens = self._tok(query)
        tokens.extend(w for w in _expand_query(query) if w not in STOPWORDS)
        return tokens

    def _idf(self, w):
        n = self.df.get(w, 0)
        return math.log(1 + (self.N - n + 0.5) / (n + 0.5))

    def _score(self, q, doc_type):
        if doc_type is not None and isinstance(doc_type, str):
            doc_type = (doc_type,)
        q = self._query_tokens(q)
        scored = []
        for i, toks in enumerate(self.corpus_tokens):
            if doc_type and self.docs[i]["type"] not in doc_type:
                continue
            tf = Counter(toks)
            s = 0.0
            for w in q:
                if w not in tf:
                    continue
                f = tf[w]
                denom = f + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl)
                s += self._idf(w) * f * (self.k1 + 1) / denom
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        return scored

    def search_with_scores(self, query, doc_type=None, topk=4):
        """返回 (文档, 原始BM25分数) 列表，供上层做弱命中判断。"""
        return [(self.docs[i], s) for s, i in self._score(query, doc_type)[:topk]]

    def search(self, query, doc_type=None, topk=4):
        return [d for d, _ in self.search_with_scores(query, doc_type, topk)]


if __name__ == "__main__":
    r = BM25Retriever()
    for q in ["外地务工人员在北京怎么申请免费法律援助", "孩子在京上学需要什么材料",
              "我被老公打了咋办", "春蕾计划怎么申请"]:
        print("Q:", q)
        print("  扩展token:", r._query_tokens(q))
        for d, s in r.search_with_scores(q):
            print("  -", round(s, 2), d["type"], d["title"][:24])
