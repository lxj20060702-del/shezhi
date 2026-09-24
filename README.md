# 她知 · 面向北京流动女性的公益垂直知识问答系统

> 华北五省（市、自治区）及港澳台大学生计算机应用大赛 · **方向一 大模型与智能体应用赛道**
> 技术路线：检索增强生成（RAG）+ 轻量公益服务知识图谱

## 一句话
面向北京流动女性的公益知识问答大模型，用垂直知识库帮她们快速获取政策、公益组织与活动等实用信息，答案可溯源。

## 快速开始（本地）
```bash
cd shezhi
python -m pip install -r requirements.txt
streamlit run app.py
# 浏览器打开 http://localhost:8501
```
未配置大模型 Key 时会自动降级为「检索式抽取答案」，一样能演示；配置免费 Key 后即切换为大模型生成式回答。

## 配置免费大模型（可选，推荐）
复制 `.env.example` 为 `.env` 并填入（或在部署平台加环境变量）：
- 智谱 GLM-4-Flash：`https://open.bigmodel.cn/api/paas/v4`（免费）
- 或硅基流动：`https://api.siliconflow.cn/v1`

## 目录结构
```
shezhi/
├─ app.py                 # Streamlit 界面（问答 / 知识图谱 / 知识库）
├─ requirements.txt
├─ data/
│  ├─ organizations.json  # 公益组织库 + 项目
│  └─ policies.json       # 政策知识库（仅权威源）
└─ src/
   ├─ kb.py               # 知识库加载
   ├─ retriever.py        # jieba + BM25 检索
   ├─ llm.py              # 大模型封装（OpenAI 兼容）
   ├─ qa.py               # RAG 问答 + 来源标注 + 降级兜底
   └─ graph.py            # 知识图谱构建
```

## 公网部署（免费）
把本仓库推到 GitHub，再在以下任一平台一键部署，获得公网 URL：
- **魔搭 ModelScope 创空间**（国内直连，推荐）
- Streamlit Community Cloud
- HuggingFace Spaces

> ⚠️ 大赛要求作品具备**公网可访问性**，仅本地/校园网访问视为无效。

## 合规与溯源
- 政策类内容一律以 gov.cn / 部门官网 / 法律法规数据库为准，标注发布机构与日期。
- 组织信息为公开脱敏资料，引用注明来源 URL 与更新时间。
