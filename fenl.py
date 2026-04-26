# -*- coding: utf-8 -*-
import os
import re
import requests
from collections import defaultdict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 分类规则
CATEGORY_PATTERNS = {
    "央视频道": re.compile(r"央视|CCTV", re.IGNORECASE),
    "卫视频道": re.compile(r"卫视|中国.*卫视", re.IGNORECASE),
    "付费频道": re.compile(r"付费|HD|高清", re.IGNORECASE),
    "电影频道": re.compile(r"电影", re.IGNORECASE),
    "数字频道": re.compile(r"数字|TV|频道", re.IGNORECASE),
}

# 省份映射
PROVINCE_MAP = {
    "京": "北京", "津": "天津", "冀": "河北", "晋": "山西", "蒙": "内蒙古",
    "辽": "辽宁", "吉": "吉林", "黑": "黑龙江",
    "沪": "上海", "苏": "江苏", "浙": "浙江", "皖": "安徽", "闽": "福建", "赣": "江西", "鲁": "山东",
    "豫": "河南", "鄂": "湖北", "湘": "湖南", "粤": "广东", "桂": "广西", "琼": "海南",
    "渝": "重庆", "川": "四川", "贵": "贵州", "云": "云南",
    "陕": "陕西", "甘": "甘肃", "青": "青海", "宁": "宁夏", "新": "新疆",
}

# 只存 频道名，实现去重
channel_classified = defaultdict(set)  # 分类: {频道名}
channel_provinces = defaultdict(set)   # 省份: {频道名}

def download_remote_m3u(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except:
        return ""

def parse_m3u_strict(content):
    channels = []
    name = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            m = re.search(r',(.+)', line)
            if m:
                name = m.group(1).strip()
        elif name and line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            channels.append(name)
            name = None
    return channels

def process_channel(name):
    # 1. 大分类
    main_cat = "地方频道"
    for cat, pat in CATEGORY_PATTERNS.items():
        if pat.search(name):
            main_cat = cat
            break
    channel_classified[main_cat].add(name)

    # 2. 省份分类
    prov = "未知省份"
    for abbr, full in PROVINCE_MAP.items():
        if full in name or abbr in name:
            prov = full
            break
    channel_provinces[prov].add(name)

def write_output():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=== 按原始分类 ===\n")
        order = ["央视频道", "卫视频道", "付费频道", "电影频道", "数字频道", "地方频道"]
        for cat in order:
            chs = channel_classified.get(cat, set())
            if chs:
                f.write(f"\n【{cat}】\n")
                for name in sorted(chs):
                    f.write(name + "\n")

        f.write("\n" + "="*40 + "\n")
        f.write("=== 按省份分类 ===\n")
        for prov in sorted(channel_provinces.keys()):
            chs = channel_provinces[prov]
            if chs:
                f.write(f"\n【{prov}】\n")
                for name in sorted(chs):
                    f.write(name + "\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        exit()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    all_names = set()
    for url in urls:
        content = download_remote_m3u(url)
        names = parse_m3u_strict(content)
        all_names.update(names)

    for name in all_names:
        process_channel(name)

    write_output()
