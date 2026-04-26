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

channel_classified = defaultdict(set)
channel_provinces = defaultdict(dict)

def download_remote_m3u(url):
    """下载远程 M3U 文件"""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"下载失败: {url} → {e}")
        return ""

def parse_m3u_strict(content):
    """严格解析 M3U：EXTINF 一行 → 链接一行"""
    channels = []
    name = None
    link = None

    lines = [l.strip() for l in content.splitlines() if l.strip()]

    for line in lines:
        if line.startswith("#EXTINF"):
            m = re.search(r',(.+)', line)
            if m:
                name = m.group(1).strip()
            continue

        if name and line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            link = line
            channels.append((name, link))
            name = None
            link = None

    return channels

def process_channel(name, link):
    # 1. 原始分类
    main_cat = "地方频道"
    for cat, pat in CATEGORY_PATTERNS.items():
        if pat.search(name):
            main_cat = cat
            break

    channel_classified[main_cat].add((name, link))

    # 2. 省份分类
    prov = "未知省份"
    for abbr, full in PROVINCE_MAP.items():
        if full in name or abbr in name:
            prov = full
            break

    channel_provinces[prov][name] = link

def write_output():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=== 按原始分类 ===\n\n")

        order = ["央视频道", "卫视频道", "付费频道", "电影频道", "数字频道", "地方频道"]
        for cat in order:
            chs = channel_classified.get(cat, set())
            if chs:
                f.write(f"【{cat}】\n")
                for n, l in sorted(chs):
                    f.write(f"{n},{l}\n")
                f.write("\n")

        f.write("="*50 + "\n")
        f.write("=== 按省份详细分类 ===\n\n")

        for prov in sorted(channel_provinces.keys()):
            chs = channel_provinces[prov]
            if chs:
                f.write(f"【{prov}】\n")
                for n, l in sorted(chs.items()):
                    f.write(f"  {n},{l}\n")
                f.write("\n")

    print(f"✅ 完成！已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print("错误：未找到 data.txt")
        exit(1)

    # 读取所有远程链接
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    if not urls:
        print("错误：data.txt 中未找到有效链接")
        exit(1)

    all_channels = []
    for url in urls:
        print(f"正在下载: {url}")
        content = download_remote_m3u(url)
        if not content:
            continue

        channels = parse_m3u_strict(content)
        print(f"↓ 解析到 {len(channels)} 个频道")
        all_channels.extend(channels)

    # 去重
    all_channels = list({link: (name, link) for name, link in all_channels}.values())

    for name, link in all_channels:
        process_channel(name, link)

    write_output()
