# -*- coding: utf-8 -*-
"""📚 知识库页（组织库 / 政策库表格 + 北京公益服务地图）

- 🎨 页面设计：改列名、列宽、展示字段（表格列定义在 ORG_COLS / POL_COLS 的字典里）
- ⚙️ 功能实现：数据在 data/organizations.json、data/policies.json；字段说明见 docs/数据源核实清单.md
"""
import streamlit as st


# ============================================================
# 🗺️ 共享顶点网格（所有16区 path 用这些点，确保拼合无缝）
#    viewBox: 0 0 600 520
# ============================================================
#   A─────B─────C─────D─────E        y≈30  最北
#   │     │     │     │     │
#  延庆  怀柔  密云  平谷   │
#   │     │     │     │     │
#   F─────G─────H─────I─────J        y≈115 北-中分界
#   │     │     │     │     │
# 门头沟  昌平   顺义   │     │
#   │     │     │     │     │
#   K─────L─────M─────N     │        y≈195 西-东分界
#   │     │     │     │     │
# 石景山  海淀  朝阳   │     │
#   │     │  ┌──┴──┐ │     │
#   │     │  │西城│ │     │
#   │     │  ├──┬──┤ │     │        y≈225-275 城六区核心
#   │     │  │东城│ │     │
#   │     │  └──┬──┘ │     │
#   │     │     │     │     │
#   S─────T─────U─────V─────W        y≈325 南-中分界
#   │     │     │     │     │
# 房山   丰台   │    通州   │
#   │     │     │     │     │
#   └─────Y─────Z─────AA────AB       y≈470 最南
#
VERTICES = {
    # 最北排
    "A": (45, 30),   "B": (225, 25),   "C": (385, 30),   "D": (510, 48),   "E": (555, 75),
    # 北-中分界
    "F": (55, 115),  "G": (235, 110),  "H": (395, 115),  "I": (520, 158),  "J": (555, 178),
    # 西-东分界
    "K": (65, 195),  "L": (245, 190),  "M": (405, 195),  "N": (525, 212),
    # 城六区核心（小网格）
    "O": (250, 225), "P": (287, 225), "Q": (322, 225), "R": (375, 225),
    "O2":(250, 275), "P2":(287, 275), "Q2":(322, 275), "R2":(375, 275),
    # 南-中分界
    "S": (75, 330),  "T": (255, 325),  "U": (380, 325),  "V": (430, 325),  "W": (530, 320),
    # 最南排
    "X": (90, 465),  "Y": (265, 475),  "Z": (400, 475),  "AA":(480, 455),  "AB":(540, 435),
}


def poly(*vnames):
    """用顶点名列表生成 SVG path d 字符串"""
    pts = [VERTICES[v] for v in vnames]
    return "M " + " L ".join(f"{x},{y}" for x, y in pts) + " Z"


# ============================================================
# 16 区数据（path 用共享顶点，确保拼合无缝）
# ============================================================
DISTRICTS = [
    # --- 北部 4 区 ---
    ("yanqing",   "延庆区",   poly("A","B","G","F"),                         0, []),
    ("huairou",   "怀柔区",   poly("B","C","H","G"),                         0, []),
    ("miyun",     "密云区",   poly("C","D","I","H"),                         0, []),
    ("pinggu",    "平谷区",   poly("D","E","J","I"),                         0, []),

    # --- 中部北 3 区 ---
    ("mentougou", "门头沟区", poly("F","G","L","K"),                         0, []),
    ("changping", "昌平区",   poly("G","H","M","L"),                         1, ["木兰花开社工中心"]),
    ("shunyi",    "顺义区",   poly("H","I","N","M"),                         0, []),

    # --- 西 1 区 ---
    ("shijingshan","石景山区",poly("K","L","O","O2","S") if False else poly("K","L","O","O2","T","S"), 0, []),

    # --- 城六区 4 区 ---
    ("haidian",   "海淀区",   poly("L","M","R","Q","P","O"),                1, ["农家女文化发展中心"]),
    ("xicheng",   "西城区",   poly("O","P","P2","O2"),                      1, ["综合公共服务"]),
    ("dongcheng","东城区",   poly("P","Q","Q2","P2"),                      1, ["综合公共服务"]),
    ("chaoyang",  "朝阳区",   poly("Q","R","R2","Q2"),                      4, ["协作者社工中心","工友之家","致诚法律援助","义联劳动法援助"]),

    # --- 西部南 1 区 ---
    ("fangshan",  "房山区",   poly("S","T","Y","X"),                        0, []),

    # --- 南部 2 区 ---
    ("fengtai",   "丰台区",   poly("O2","R2","U","T","Y")[:len(poly("O2","R2","U","T"))], 0, []),
    ("daxing",    "大兴区",   poly("T","U","Z","Y"),                         0, []),

    # --- 东部 1 区 ---
    ("tongzhou",  "通州区",   poly("U","V","W","AA","Z"),                  0, []),
]
# 上面几个区用了临时写法，下面修正
# ============================================================

# 修正版：重新定义所有区，确保每个 path 简洁且拼合
# 石景山: K-L-O-O2-S-T ? 不，用简单四边形
# 实际上让我完全重新写一遍，每个区都是干净的多边形

DISTRICTS = [
    # 北部
    ("yanqing",   "延庆区",   poly("A","B","G","F"),      0, []),
    ("huairou",   "怀柔区",   poly("B","C","H","G"),      0, []),
    ("miyun",     "密云区",   poly("C","D","I","H"),      0, []),
    ("pinggu",    "平谷区",   poly("D","E","J","I"),      0, []),

    # 中北
    ("mentougou", "门头沟区", poly("F","G","L","K"),      0, []),
    ("changping", "昌平区",   poly("G","H","M","L"),      1, ["木兰花开社工中心"]),
    ("shunyi",    "顺义区",   poly("H","I","N","M"),      0, []),

    # 城西
    ("shijingshan","石景山区",poly("K","L","O","O2","S"),0, []),

    # 城六区
    ("haidian",   "海淀区",   poly("L","M","R","O"),      1, ["农家女文化发展中心"]),
    ("xicheng",   "西城区",   poly("O","P","P2","O2"),   1, ["综合公共服务"]),
    ("dongcheng","东城区",   poly("P","Q","Q2","P2"),   1, ["综合公共服务"]),
    ("chaoyang",  "朝阳区",   poly("Q","R","R2","Q2"),   4, ["协作者社工中心","工友之家","致诚法律援助","义联劳动法援助"]),

    # 城南西
    ("fangshan",  "房山区",   poly("S","O2","T","Y","X"),0, []),

    # 城南
    ("fengtai",   "丰台区",   poly("O2","R2","U","T"),   0, []),
    ("daxing",    "大兴区",   poly("T","U","Z","Y"),      0, []),

    # 城东
    ("tongzhou",  "通州区",   poly("R2","V","W","AA","Z","U"), 0, []),
]


# ============================================================
# 🎨 粉色系配色阶梯（柔和、女性向、和谐）
# ============================================================
# 5 级：0(无) → 1 → 2 → 3 → 4+(最多)
COLOR_STEPS = [
    "#fde8ec",  # 0  极浅粉（接近白）
    "#f8cdd6",  # 1  柔粉
    "#f0a8b7",  # 2  樱花粉
    "#e07f97",  # 3  玫瑰粉
    "#c95676",  # 4+ 深玫红
]


def _count_to_color(n):
    if n <= 0: return COLOR_STEPS[0]
    if n == 1: return COLOR_STEPS[1]
    if n == 2: return COLOR_STEPS[2]
    if n == 3: return COLOR_STEPS[3]
    return COLOR_STEPS[4]


def _centroid(path_d):
    """从 M x1,y1 L x2,y2 ... Z 计算多边形中心"""
    coords = []
    raw = path_d.replace("M ", "").replace("Z", "").strip()
    for part in raw.split(" L "):
        if "," in part:
            x, y = part.split(",")
            coords.append((float(x), float(y)))
    if not coords:
        return 300, 260
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _map_svg():
    """生成粉色系 Choropleth 北京地图"""
    polygons = ""
    labels = ""
    cards_html = ""

    for did, name, path_d, count, services in DISTRICTS:
        cx, cy = _centroid(path_d)
        fill = _count_to_color(count)

        # polygon（白色描边 + round join 柔化棱角）
        polygons += (
            f'<path class="bj-district" data-id="{did}" '
            f'd="{path_d}" fill="{fill}" '
            f'stroke="#fff" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round" '
            f'stroke-miterlimit="1" '
            f'data-count="{count}"/>'
        )

        # 区名标签（在多边形中心，带白色文字描边确保可读）
        labels += (
            f'<text x="{cx}" y="{cy+4}" class="bj-label">{name}</text>'
        )

        # 下方统计卡片
        has_data = count > 0
        srv_html = ""
        for s in services[:3]:
            srv_html += f'<div class="bj-dc-srv">· {s}</div>'
        cls = "bj-dc" if has_data else "bj-dc bj-dc-empty"
        cards_html += (
            f'<div class="{cls}" style="border-left:3px solid {fill}">'
            f'<div class="bj-dc-name">{name}</div>'
            f'<div class="bj-dc-count">{count} 家公益组织</div>'
            f'{srv_html}'
            f'</div>'
        )

    svg = (
        f'<svg class="bj-map-svg" viewBox="0 0 600 520" xmlns="http://www.w3.org/2000/svg">'
        f'{polygons}'
        f'{labels}'
        f'</svg>'
    )

    # 粉色渐变色阶梯图例
    legend = (
        '<div class="bj-legend">'
        '<span class="bj-legend-label">公益组织数量</span>'
        '<span class="bj-legend-min">0</span>'
        '<div class="bj-legend-bar" style="background:linear-gradient(to right, '
        '#fde8ec, #f8cdd6, #f0a8b7, #e07f97, #c95676)"></div>'
        '<span class="bj-legend-max">4+</span>'
        '</div>'
    )

    return (
        '<div class="bj-map-card">'
        '<p class="bj-map-title">🗺️ 北京市公益服务地图</p>'
        '<p class="bj-map-desc">16 区公益组织密度分布 · 颜色越深表示已收录机构越多</p>'
        f'{svg}'
        f'{legend}'
        f'<div class="bj-district-cards">{cards_html}</div>'
        '</div>'
    )


def render(orgs, policies):
    st.subheader("公益组织库")
    st.dataframe(
        [{"名称": o["name"], "服务对象": o.get("target", ""),
          "核心服务/活动": "、".join(o.get("services", []) + o.get("activities", []))[:60],
          "来源": o.get("source_name", "")} for o in orgs],
        use_container_width=True)

    st.subheader("政策知识库")
    st.dataframe(
        [{"主题": p.get("topic", ""), "标题": p.get("title", ""),
          "发布机构": p.get("publisher", ""),
          "生效/更新": p.get("effective_date", "") or p.get("updated", "")} for p in policies],
        use_container_width=True)

    # 北京公益服务地图
    st.markdown("---")
    st.markdown("### 🗺️ 北京市公益服务地图")
    try:
        st.markdown(_map_svg(), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"地图渲染失败：{e}")
        st.code(_map_svg()[:500])

    st.caption("数据均为公开信息，逐条核实；引用需注明出处（详见 docs/数据源核实清单.md）。")
