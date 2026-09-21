# 协作规范（4 人并行开发）· CONTRIBUTING

> 目标：4 个人同时改，**尽量不撞车**。核心思路是「**一人一个文件**」。
> 线上地址：https://shezhi.streamlit.app ｜ 仓库：https://github.com/lxj20060702-del/shezhi

---

## 一、谁改哪个文件（先看这张表）

| 角色 | 你负责的文件 | 主要任务 |
|---|---|---|
| 🎨 设计 A | `views/qa_view.py`、`views/kb_view.py`、`assets/style.css` | 问答页 + 知识库页的视觉；**全站配色/字体/卡片样式** |
| 🎨 设计 B | `views/recommend_view.py`、`views/graph_view.py` | 推荐页 + 图谱页的视觉；手机端布局 |
| ⚙️ 功能 A | `src/qa.py`、`src/retriever.py`、`src/llm.py`、`data/policies.json` | 问答准确率、**政策库扩充**（必须官方源） |
| ⚙️ 功能 B | `src/recommend.py`、`src/graph.py`、`data/organizations.json` | 推荐算法、**组织字段补齐**、图谱关系 |
| 👑 组长（雪娇） | `app.py`、`requirements.txt`、`docs/`、`tests/` | 接线（新页面）、合并 PR、部署、文档/视频/报名 |

> 只改自己那份文件，就不用怕覆盖别人的改动。
> 需要改别人负责的文件？**先群里说一声**，别直接改。

---

## 二、目录地图（改哪里，一目了然）

```
shezhi/
├── app.py               入口：页面配置 / 样式加载 / 侧边栏 / 标签页分发  ← 👑 组长
├── assets/style.css     全站样式：配色变量、卡片、字号、手机适配        ← 🎨 设计 A
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
├── tests/smoke_test.py  冒烟测试（改完先跑它）                    ← 所有人可用
└── docs/                需求文档、数据源清单、接力说明
```

---

## 三、怎么改（3 个真实例子）

**例 1：想把主色从绿色改成紫色**
```css
/* assets/style.css 顶部 */
:root { --brand: #7c5cd6; }   /* 只改这一行，全站跟着变 */
```

**例 2：想给「为你推荐」加一个「附近」筛选**
- 先加数据：`data/organizations.json` 里给机构加 `"district": "朝阳区"`（⚙️ 功能 B）
- 再加 UI：`views/recommend_view.py` 加一个 `st.selectbox` 按区筛选（🎨 设计 B）
- 两人改的是不同文件，可以同时进行 —— 这叫「**接口先行**」：先在群里说好字段名 `district`

**例 3：想新增一个页面（比如「数据后台」）**
1. 新建 `views/admin_view.py`，里面写 `def render(): ...`
2. `app.py` 里加一行：`from views import admin_view`，再加 `t_admin, = st.tabs([...])` 分发
   （⚠️ `app.py` 只有组长改，其他人提需求）

---

## 四、改完怎么上线（Git 流程）

```bash
# 0. 第一次：把仓库克隆下来
git clone https://github.com/lxj20060702-del/shezhi.git
cd shezhi
pip install -r requirements.txt

# 1. 每次开工前先拉最新（重要！）
git pull origin main

# 2. 本地自测
streamlit run app.py            # 浏览器 http://localhost:8501
python tests/smoke_test.py      # 冒烟测试必须过

# 3. 开一个自己的分支（不要直接推 main）
git checkout -b feat/设计A-问答页美化

# 4. 提交并推送
git add -A
git commit -m "style: 问答页按钮与卡片改版"
git push origin feat/设计A-问答页美化

# 5. 去 GitHub 开 Pull Request（PR）→ 组长 review + 合并到 main
#    main 一合并，Streamlit Cloud 会在约 1 分钟内自动重新部署
```

**为什么必须走分支 + PR？** 4 个人都直接推 `main`，很容易互相覆盖、JSON 冲突解不开。走 PR 还能顺手 review。

---

## 五、让 3 个队友能提交代码（一次性设置）

**方式 A（推荐，组内协作）**
1. 组长打开 https://github.com/lxj20060702-del/shezhi → **Settings → Collaborators → Add people**
2. 输入队友的 **GitHub 用户名**（或邮箱）→ 邀请 → 队友邮箱点接受
3. 之后大家就能对这个仓库开分支、推代码、提 PR

**方式 B（不想给写权限）**
队友点仓库右上角 **Fork** 到自己账号 → 改完向原仓库提 PR。

> 队友只需要 **GitHub 账号**。要登 Streamlit Cloud / 改 Secrets，才需要组长的账号（一般用不上）。

---

## 六、避坑清单（血泪版）

- 🚫 **绝不提交 `.env`**（里面是大模型 Key；`.gitignore` 已挡）；Key 也绝不写进代码（**仓库是 public**）
- 🚫 不要直接推 `main`；一律 分支 → PR
- 🚫 **两个设计同学不要同时改 `app.py`**（只有组长改）
- 🚫 **同一时间只有一个人改同一个 JSON**（JSON 冲突极难解）；分好坏：`policies.json`=功能A，`organizations.json`=功能B
- ✅ 改完 `data/*.json` 先校验格式：
  ```bash
  python -c "import json;json.load(open('data/policies.json',encoding='utf-8'));print('ok')"
  ```
- ✅ 本地 `streamlit run app.py` 能跑 + `python tests/smoke_test.py` 通过，再提 PR
- ✅ 加了第三方库，记得同步写进 `requirements.txt`（否则云端会报 ModuleNotFoundError）
- ✅ 政策类内容**只能用官方源**（gov.cn / 部门官网 / 法律法规数据库），并标注发布机构 + 生效日期 + 链接
- ⚠️ 顺手项：`use_container_width` 将在 2025-12-31 后被移除，建议慢慢改成 `width="stretch"`

---

## 七、遇到问题怎么办

1. 先看本地报错信息（`streamlit run` 的终端窗口会打印 traceback）
2. 看 `docs/` 里的需求文档，确认字段/口径要求
3. 群里问；或让组长问 Baby（AI 助手）——她能直接改代码、跑测试、推送部署
