# -*- coding: utf-8 -*-
import os
import re
import requests
from collections import defaultdict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

def download_m3u(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except:
        return ""

def parse_m3u_raw(content):
    """
    严格按 M3U 原始结构解析：
    得到原始分类 → 频道名 的结构
    完全不改动原始分类名
    """
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    categories = defaultdict(set)
    current_category = None
    current_name = None

    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
        elif line.startswith("#EXTINF"):
            # 尝试从 EXTINF 提取频道名
            m = re.search(r',(.+)', line)
            if m:
                current_name = m.group(1).strip()
            continue
        elif line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            if current_name:
                # 遇到链接 → 说明一个频道结束
                if current_category:
                    categories[current_category].add(current_name)
                current_name = None
                continue
        elif line.startswith("#"):
            # 原始 M3U 中 # 开头的可能是分组名
            cat = line.replace("#", "").strip()
            if cat:
                current_category = cat
            continue

    return categories

def write_horizontal(categories, f):
    """
    横向排列：
    分类名 → 频道名1 | 频道名2 | 频道名3 | ...
    自动换行
    自动去重
    无链接
    """
    for cat in sorted(categories.keys()):
        channels = sorted(categories[cat])
        if channels:
            line = f"{cat} → " + " | ".join(channels)
            f.write(line + "\n\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    all_cats = defaultdict(set)

    for url in urls:
        content = download_m3u(url)
        if not content:
            continue

        raw_cats = parse_m3u_raw(content)
        for cat, chans in raw_cats.items():
            all_cats[cat].update(chans)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_horizontal(all_cats, f)

    print(f"✅ 完成！结果写入: {OUTPUT_FILE}")
