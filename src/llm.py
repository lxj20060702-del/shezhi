# -*- coding: utf-8 -*-
"""大模型封装：OpenAI 兼容接口（智谱 GLM-4-Flash 免费 / 硅基流动等）。
未配置 key 时返回 None，交由上层降级为“检索式抽取答案”。"""
import os
from pathlib import Path


def _load_dotenv():
    """极简 .env 加载（项目根目录），不依赖第三方库。"""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


class LLM:
    def __init__(self,
                 base_url=None, api_key=None, model=None, disabled=None):
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "glm-4-flash")
        env_disabled = os.getenv("LLM_DISABLED", "false").lower() in ("1", "true", "yes")
        self.disabled = disabled if disabled is not None else env_disabled
        self.client = None
        if self.api_key and not self.disabled:
            try:
                from openai import OpenAI
                self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            except Exception:
                self.client = None

    @property
    def available(self):
        return self.client is not None

    def chat(self, system, user, temperature=0.2, max_tokens=900):
        if not self.available:
            return None
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
                temperature=temperature, max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[大模型调用失败，已降级为检索结果] {e}"
