# -*- coding: utf-8 -*-
"""轻量检索：jieba 分词 + BM25，本地零依赖、零成本。"""
import math
from collections import Counter

import jieba

import kb


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

    @staticmethod
    def _tok(s):
        return [w for w in jieba.lcut_for_search(s) if w.strip()]

    def _idf(self, w):
        n = self.df.get(w, 0)
        return math.log(1 + (self.N - n + 0.5) / (n + 0.5))

    def search(self, query, doc_type=None, topk=4):
        q = self._tok(query)
        scores = []
        for i, toks in enumerate(self.corpus_tokens):
            if doc_type and self.docs[i]["type"] != doc_type:
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
                scores.append((s, i))
        scores.sort(reverse=True)
        return [self.docs[i] for _, i in scores[:topk]]


if __name__ == "__main__":
    r = BM25Retriever()
    for q in ["外地务工人员在北京怎么申请免费法律援助", "孩子在京上学需要什么材料", "往年办过哪些女性文艺活动"]:
        print("Q:", q)
        for d in r.search(q):
            print("  -", d["type"], d["title"], round(0, 2))
