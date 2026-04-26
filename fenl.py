import os
import re
import requests

DATA_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
MAX_LINE = 80

PROVINCES = [
    "北京","上海","天津","重庆","广东","广西","江苏","浙江","山东","山西","河南","河北",
    "湖北","湖南","安徽","江西","福建","海南","四川","云南","陕西","甘肃","青海","宁夏","新疆",
    "内蒙古","黑龙江","吉林","辽宁","香港","澳门","台湾","贵州"
]

SATELLITE = [p + "卫视" for p in PROVINCES]
PAY_CHANNEL = ["欢笑剧场","都市剧场","精品","CHC","动作电影","家庭影院","影迷电影","高清电影","影院"]
DIGITAL = ["CCTV5+","CCTV17","数字","纪实","科教","卡通","少儿","新闻","法治","音乐"]

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

def parse_m3u(text):
    """解析 M3U 格式频道名"""
    channels = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            m = re.search(r"#EXTINF:-1,(.+)", line)
            if m:
                name = m.group(1).strip()
                channels.append(name)
                log(f"解析频道：{name}")
    return channels

def classify(name):
    upper = name.upper()

    if "CCTV" in upper or "央视" in name:
        return "央视频道"

    for s in SATELLITE:
        if s in name:
            return "卫视频道"

    if any(k in name for k in PAY_CHANNEL):
        return "付费频道"

    if "CHC" in upper or "电影" in name:
        return "电影频道"

    if any(k in name for k in DIGITAL):
        return "数字频道"

    for prov in PROVINCES:
        if prov in name:
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
            chs = parse_m3u(text)
            all_channels.extend(chs)

    log(f"解析到频道（含重复）：{len(all_channels)} 个")

    # ⭐⭐⭐ 强力去重（保持顺序）
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

    order = ["央视频道","卫视频道","付费频道","电影频道","数字频道"]

    for key in order:
        if key in groups:
            output.append(format_horizontal(key, groups[key]))
            output.append("")

    for key in sorted(groups.keys()):
        if key.startswith("地方频道-"):
            output.append(format_horizontal(key, groups[key]))
            output.append("")

    if "未知频道" in groups:
        output.append(format_horizontal("未知频道", groups["未知频道"]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    log(f"✔ 分类完成 → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
