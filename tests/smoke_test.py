# -*- coding: utf-8 -*-
"""用 Streamlit AppTest 做端到端冒烟测试（能抓出运行时异常）"""
import sys
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py", default_timeout=60)
at.run()
print("首屏 exception:", at.exception)
assert not at.exception, at.exception

# 注入一个画像，触发「为你推荐」渲染
at.session_state["rec_profile"] = {
    "gender": "女", "jobs": ["家政 / 保洁"],
    "needs": ["被欠薪 / 劳动纠纷要维权", "孩子上学 / 带娃"], "has_child": True,
}
at.run()
print("推荐页 exception:", at.exception)
assert not at.exception, at.exception

# 抓一下页面上的 markdown / 成功提示，确认真的渲染了
succ = [b.value for b in at.success]
infos = [b.value for b in at.info]
print("success 提示:", succ[:1])
md = [m.value for m in at.markdown if "class=\"rec\"" in m.value]
print("推荐卡片数:", len(md))
first = (md[0][:160].replace("\n", " ") if md else "无")
print("第一张卡片片段:", first.encode("utf-8", "replace").decode("utf-8", "replace"))

# 全空画像 -> 兜底
at.session_state["rec_profile"] = {"gender": "", "jobs": [], "needs": [], "has_child": False}
at.run()
print("兜底 exception:", at.exception)
assert not at.exception
caps = [c.value for c in at.caption if "没有精确命中" in c.value]
print("兜底提示:", caps[:1])
print("APP 冒烟测试通过 ✅")
