import os
import requests
import re

DATA_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
MAX_LINE = 80

# 全国省份
PROVINCES = [
    "北京","上海","天津","重庆","广东","广西","江苏","浙江","山东","山西","河南","河北",
    "湖北","湖南","安徽","江西","福建","海南","四川","云南","陕西","甘肃","青海","宁夏","新疆",
    "内蒙古","黑龙江","吉林","辽宁","香港","澳门","台湾","贵州"
]

def log(msg):
    print(f"[LOG] {msg}", flush=True)

def download(url):
    log(f"下载：{url}")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log(f"❌ 下载失败：{e}")
        return ""

def parse_txt(text):
    """解析 TXT 格式：频道名,URL"""
    channels = []
    for line in text.splitlines():
        line = line.strip()
        if "," in line:
            name = line.split(",", 1)[0].strip()
            if name and not name.startswith("#"):
                channels.append(name)
                log(f"解析频道：{name}")
    return channels

def extract_province(name):
    """频道名以省份开头"""
    for prov in PROVINCES:
        if name.startswith(prov):
            return prov
    return None

def extract_city(name, prov):
    """
    提取地市：
    规则：频道名以 2~4 个汉字开头，且不是省份名
    """
    m = re.match(r"^([\u4e00-\u9fa5]{2,4})", name)
    if m:
        city = m.group(1)
        if city != prov:
            return city
    return None

def classify(name):
    prov = extract_province(name)
    if prov:
        city = extract_city(name, prov)
        if city:
            return f"地方频道-{prov}-{city}"
        return f"地方频道-{prov}"

    return "未知频道"

def format_horizontal(name, items):
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

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        urls = [x.strip() for x in f if x.strip()]

    log(f"读取到 {len(urls)} 个链接")

    all_channels = []

    for url in urls:
        text = download(url)
        if text:
            chs = parse_txt(text)
            all_channels.extend(chs)

    log(f"解析到频道（含重复）：{len(all_channels)} 个")

    # 去重
    all_channels = list(dict.fromkeys(all_channels))
    log(f"去重后频道数：{len(all_channels)}")

    groups = {}

    for ch in all_channels:
        c = classify(ch)
        log(f"分类：{ch} → {c}")
        groups.setdefault(c, []).append(ch)

    for k in groups:
        groups[k].sort()

    output = []

    # 省级频道
    for prov in PROVINCES:
        key = f"地方频道-{prov}"
        if key in groups:
            output.append(format_horizontal(key, groups[key]))
            output.append("")

    # 地市频道
    for key in sorted(groups.keys()):
        if key.count("-") == 2:  # 地方频道-省-市
            output.append(format_horizontal(key, groups[key]))
            output.append("")

    # 未知频道
    if "未知频道" in groups:
        output.append(format_horizontal("未知频道", groups["未知频道"]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    log(f"✔ 分类完成 → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
