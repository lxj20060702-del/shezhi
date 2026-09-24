# 协作规范（4 人并行开发）· CONTRIBUTING

> **全部在线上完成，不需要装任何软件**（不用 Python、不用 git 命令行、不用 clone 代码）。
> 线上地址：https://shezhi.streamlit.app ｜ 仓库：https://github.com/lxj20060702-del/shezhi
> 新队友先看：`docs/线上协作指南.md`

---

## 一、谁改哪个文件（先看这张表）

| 角色 | 你负责的文件 | 主要任务 |
|---|---|---|
| 🎨 设计 A | `assets/style.css`、`.streamlit/config.toml`、`views/qa_view.py`、`views/kb_view.py` | 全站配色/字体/卡片；问答页 + 知识库页 |
| 🎨 设计 B | `views/recommend_view.py`、`views/graph_view.py` | 推荐页 + 图谱页；手机端布局 |
| ⚙️ 功能 A | `src/qa.py`、`src/retriever.py`、`src/llm.py`、`data/policies.json` | 问答准确率、**政策库扩充**（必须官方源） |
| ⚙️ 功能 B | `src/recommend.py`、`src/graph.py`、`data/organizations.json` | 推荐算法、**组织字段补齐**、图谱关系 |
| 👑 组长（雪娇） | `app.py`、`requirements.txt`、`docs/`、`tests/` | 接线（新页面）、合并 PR、部署、文档/视频/报名 |

> 核心规则：**只改自己那份文件**；要动别人的先群里说；`app.py` 只有组长改。

---

## 二、目录地图（改哪里，一目了然）

```
shezhi/
├── app.py               入口：页面配置 / 样式加载 / 侧边栏 / 标签页分发  ← 👑 组长
├── assets/style.css     全站样式：配色变量、卡片、字号、手机适配        ← 🎨 设计 A
├── .streamlit/config.toml 整体主题（浅色 + 主色）                      ← 🎨 设计 A
├── views/               每个标签页一个文件（各管一个，互不冲突）
│   ├── qa_view.py           💬 智能问答页                        ← 🎨 设计 A
│   ├── recommend_view.py    🎯 为你推荐页                        ← 🎨 设计 B
│   ├── graph_view.py        🕸️ 知识图谱页                        ← 🎨 设计 B
│   └── kb_view.py           📚 知识库页                          ← 🎨 设计 A
├── src/                 业务逻辑
│   ├── qa.py / retriever.py / llm.py   问答链路（RAG）           ← ⚙️ 功能 A
│   ├── recommend.py                    个性化推荐算法            ← ⚙️ 功能 B
│   └── graph.py / kb.py                图谱构建 / 数据加载        ← ⚙️ 功能 B
├── data/                知识库数据（JSON）
│   ├── policies.json        政策库（3 条，要扩）                  ← ⚙️ 功能 A
│   └── organizations.json   组织库（7 家 + 1 项目）               ← ⚙️ 功能 B
├── tests/smoke_test.py  冒烟测试（能跑就跑，跑不了交给组长）      ← 所有人
└── docs/                需求文档、数据源清单、线上协作指南
```

---

## 三、线上改法（推荐，零安装）

### 路径 A：网页直接改（最简单，适合改一个文件）
1. 打开 https://github.com/lxj20060702-del/shezhi
2. 点进要改的文件 → 右上角 **✏️ 铅笔** → 改内容
3. 底部 **Commit changes**：写一句说明，选 **`Create a new branch for this commit and start a pull request`**
   → **Propose changes** → **Create pull request**

### 路径 B：网页版 VS Code（改多个文件更舒服）
1. 打开 **https://github.dev/lxj20060702-del/shezhi**（浏览器里就是 VS Code）
2. 改完 **Ctrl+Shift+G** → 填说明 → **Commit** → 选 **Create a new branch**
3. 回仓库页点 **Compare & pull request** → **Create pull request**

### 改完怎么上线
组长在 PR 页面 **Merge pull request** → Streamlit Cloud **约 1 分钟自动重新部署** → 刷新线上地址即生效。
改坏了组长点 **Revert** 一键回退。

### 让队友能提交（组长一次性设置）
仓库 **Settings → Collaborators → Add people** → 填队友 GitHub 用户名 → 队友邮箱接受邀请。
（不想给写权限：队友 **Fork** 后提 PR，流程一样。）

---

## 四、本机开发（可选，想本地调试才用）

```bash
git clone https://github.com/lxj20060702-del/shezhi.git && cd shezhi
pip install -r requirements.txt
streamlit run app.py           # http://localhost:8501
python tests/smoke_test.py     # 冒烟测试
```
本地调试需要在根目录建 `.env`（**不要提交**）：`LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`。
日常改样式/文案/数据，**用线上路径就够了**。

---

## 五、常用改动示例

**① 换主色（设计 A）**：`assets/style.css` 顶部 `:root { --brand: #6da34d; }` 改色；同步 `.streamlit/config.toml` 的 `primaryColor`。

**② 换问答页示例问题（设计 A）**：`views/qa_view.py` 里的 `EXAMPLES` 列表。

**③ 加一条政策（功能 A）**：`data/policies.json` 照现有条目加一条，字段：

```json
{
  "id": "pol_xxx",
  "topic": "社保医保 | 劳动维权 | 居住证 | …",
  "title": "政策名称",
  "publisher": "发布机构（政府部门）",
  "effective_date": "YYYY-MM-DD",
  "summary": "用大白话写 2–3 句，面向看不懂政策的打工人",
  "source_name": "官网名",
  "source_url": "https://…",
  "updated": "2026-09-21"
}
```
⚠️ 来源只能用官方（gov.cn / 部门官网 / 法律法规数据库）；JSON 每条之间逗号、最后一条不加逗号；
GitHub 编辑器出现**红色波浪线**说明格式错了，别提交。

**④ 给机构补字段（功能 B）**：`data/organizations.json` 补 `"intro"`（简介）与 `"join"`（怎么参与）。

**⑤ 新增页面**：队友写 `views/xxx_view.py`（`def render(): ...`），组长在 `app.py` 加导入 + 一个 `st.tabs` 项。

---

## 六、避坑清单

- 🚫 **绝不提交密钥 / Key**（仓库是 public）；`.env` 已在 `.gitignore`，别强行加
- 🚫 **不直接改 `main`**；一律「新建分支 → PR」
- 🚫 **不要改 `app.py`**（组长专属）
- 🚫 **同一时间只有一个人改同一个 JSON**（冲突极难解）：`policies.json`=功能A，`organizations.json`=功能B
- ✅ 改 JSON 后检查红色波浪线；不确定就把片段发群里
- ✅ 加了第三方库（Python 包）必须同步写进 `requirements.txt`，否则云端报 ModuleNotFoundError
- ✅ 政策类内容只用官方源，标注发布机构 + 生效日期 + 链接（评审重点）
- ⚠️ 顺手项：`use_container_width` 将在 2025-12-31 后被移除，慢慢改成 `width="stretch"`
