import os
import re
import requests

DATA_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
MAX_LINE = 80

# 省份关键字
PROVINCES = [
    "贵州","北京","上海","天津","重庆","广东","广西","江苏","浙江","山东","山西","河南","河北",
    "湖北","湖南","安徽","江西","福建","海南","四川","云南","陕西","甘肃","青海","宁夏","新疆",
    "内蒙古","黑龙江","吉林","辽宁","香港","澳门","台湾"
]

# 付费频道关键词
PAY_CHANNEL_KEYWORDS = [
    "欢笑剧场","都市剧场","精品","CHC","动作电影","家庭影院","影迷电影","高清电影","影院"
]

# 数字频道关键词
DIGITAL_KEYWORDS = [
    "CCTV5+","CCTV17","数字","纪实","科教","卡通","少儿","新闻","法治","音乐"
]

def download_m3u(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except:
        print(f"下载失败：{url}")
        return ""

def extract_channels(m3u_text):
    channels = []
    for line in m3u_text.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            match = re.search(r"#EXTINF:-1,(.+)", line)
            if match:
                name = match.group(1).strip()
                channels.append(name)
    return channels

def classify_channel(name):
    n = name.upper()

    # 央视频道
    if "CCTV" in n or "央视" in name:
        return "央视频道"

    # 付费频道
    if any(k in name for k in PAY_CHANNEL_KEYWORDS):
        return "付费频道"

    # 卫视频道
    if "卫视" in name:
        return "卫视频道"

    # 电影频道（CHC 优先）
    if "CHC" in n:
        return "电影频道_CHC"
    if "电影" in name:
        return "电影频道"

    # 数字频道
    if any(k in name for k in DIGITAL_KEYWORDS):
        return "数字频道"

    # 地方频道（按省份）
    for prov in PROVINCES:
        if prov in name:
            return f"地方频道_{prov}"

    return "其它频道"

def format_horizontal(name, items):
    lines = []
    line = name + "："

    for item in items:
        if len(line) + len(item) + 1 > MAX_LINE:
            lines.append(line)
            line = " " * (len(name) + 1) + item
        else:
            line += " " + item

    lines.append(line)
    return "\n".join(lines)

def main():
    if not os.path.exists(DATA_FILE):
        print("缺少 data.txt")
        return

    # 读取 URL 列表
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        urls = [x.strip() for x in f if x.strip()]

    all_channels = []

    # 下载并解析
    for url in urls:
        print(f"下载：{url}")
        text = download_m3u(url)
        if text:
            all_channels.extend(extract_channels(text))

    # 分类容器
    groups = {
        "央视频道": [],
        "付费频道": [],
        "卫视频道": [],
        "电影频道_CHC": [],
        "电影频道": [],
        "数字频道": [],
        "地方频道_贵州": [],  # 贵州优先
    }

    # 其它省份地方频道
    other_province_groups = {}

    # 分类
    for ch in all_channels:
        c = classify_channel(ch)

        if c.startswith("地方频道_"):
            prov = c.split("_")[1]
            if prov == "贵州":
                groups["地方频道_贵州"].append(ch)
            else:
                other_province_groups.setdefault(prov, []).append(ch)
        else:
            groups.setdefault(c, []).append(ch)

    # 排序
    groups["电影频道_CHC"].sort()
    groups["电影频道"].sort()
    groups["央视频道"].sort()
    groups["付费频道"].sort()
    groups["卫视频道"].sort()
    groups["数字频道"].sort()
    groups["地方频道_贵州"].sort()

    # 其它省份按拼音排序
    sorted_provinces = sorted(other_province_groups.keys())

    # 输出
    output_lines = []

    # 固定分类顺序
    order = [
        "央视频道",
        "付费频道",
        "卫视频道",
        "电影频道_CHC",
        "电影频道",
        "数字频道",
        "地方频道_贵州"
    ]

    for key in order:
        if groups[key]:
            display_name = key.replace("_CHC", "")
            output_lines.append(format_horizontal(display_name, groups[key]))
            output_lines.append("")

    # 其它省份
    for prov in sorted_provinces:
        items = sorted(other_province_groups[prov])
        output_lines.append(format_horizontal(f"地方频道-{prov}", items))
        output_lines.append("")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\n分类完成 → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
