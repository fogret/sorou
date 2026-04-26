import os
import re

DATA_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
MAX_LINE = 80

# 省份关键字
PROVINCES = [
    "北京","上海","天津","重庆","广东","广西","江苏","浙江","山东","山西","河南","河北",
    "湖北","湖南","安徽","江西","福建","海南","四川","云南","陕西","甘肃","青海","宁夏","新疆",
    "内蒙古","黑龙江","吉林","辽宁","香港","澳门","台湾","贵州"
]

# 卫视关键词
SATELLITE = [p + "卫视" for p in PROVINCES]

# 付费频道关键词
PAY_CHANNEL = ["欢笑剧场","都市剧场","精品","CHC","动作电影","家庭影院","影迷电影","高清电影","影院"]

# 数字频道关键词
DIGITAL = ["CCTV5+","CCTV17","数字","纪实","科教","卡通","少儿","新闻","法治","音乐"]


def log(msg):
    print(f"[LOG] {msg}", flush=True)


def parse_line(line):
    """解析频道名和 URL"""
    if "," not in line:
        log(f"跳过无效行：{line}")
        return None, None
    name, url = line.split(",", 1)
    return name.strip(), url.strip()


def classify(name):
    """根据频道名自动分类"""

    upper = name.upper()

    # CCTV
    if "CCTV" in upper or "央视" in name:
        return "央视频道"

    # 卫视
    for s in SATELLITE:
        if s in name:
            return "卫视频道"

    # 付费频道
    if any(k in name for k in PAY_CHANNEL):
        return "付费频道"

    # 电影频道
    if "CHC" in upper or "电影" in name:
        return "电影频道"

    # 数字频道
    if any(k in name for k in DIGITAL):
        return "数字频道"

    # 地方频道（自动识别省份）
    for prov in PROVINCES:
        if prov in name:
            return f"地方频道-{prov}"

    return "未知频道"


def format_horizontal(name, items):
    """横向输出，逗号分隔，自动换行"""
    lines = []
    line = name + "："

    for item in items:
        part = item + ", "
        if len(line) + len(part) > MAX_LINE:
            lines.append(line.rstrip(", "))
            line = " " * (len(name) + 1) + part
        else:
            line += part

    lines.append(line.rstrip(", "))
    return "\n".join(lines)


def main():
    if not os.path.exists(DATA_FILE):
        log("❌ data.txt 不存在")
        return

    log("读取 data.txt ...")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = [x.strip() for x in f if x.strip()]

    log(f"读取到 {len(lines)} 行")

    channels = []

    for line in lines:
        name, url = parse_line(line)
        if name:
            channels.append(name)
            log(f"解析频道：{name}")

    log(f"共解析到频道：{len(channels)} 个")

    # 去重
    channels = list(dict.fromkeys(channels))
    log(f"去重后频道数：{len(channels)}")

    groups = {}

    for ch in channels:
        c = classify(ch)
        log(f"分类：{ch} → {c}")
        groups.setdefault(c, []).append(ch)

    # 排序
    for k in groups:
        groups[k].sort()

    # 输出
    output = []

    # 固定顺序
    order = [
        "央视频道",
        "卫视频道",
        "付费频道",
        "电影频道",
        "数字频道",
    ]

    for key in order:
        if key in groups:
            log(f"{key} 数量：{len(groups[key])}")
            output.append(format_horizontal(key, groups[key]))
            output.append("")

    # 地方频道
    for key in sorted(groups.keys()):
        if key.startswith("地方频道-"):
            log(f"{key} 数量：{len(groups[key])}")
            output.append(format_horizontal(key, groups[key]))
            output.append("")

    # 未知频道
    if "未知频道" in groups:
        log(f"未知频道 数量：{len(groups['未知频道'])}")
        output.append(format_horizontal("未知频道", groups["未知频道"]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    log(f"✔ 分类完成 → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
