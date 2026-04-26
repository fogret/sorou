# -*- coding: utf-8 -*-
import os
import re
import requests
from collections import defaultdict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

def log(msg):
    """只保留必要运行日志，干净不干扰输出"""
    print(f"[INFO] {msg}")

def download_m3u(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log(f"下载失败：{url} → {str(e)}")
        return ""

def parse_m3u_raw(content):
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    categories = defaultdict(set)
    current_cat = None
    current_name = None

    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
        elif line.startswith("#EXTINF"):
            m = re.search(r',(.+)', line)
            if m:
                current_name = m.group(1).strip()
            continue
        elif line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            if current_name and current_cat:
                categories[current_cat].add(current_name)
                current_name = None
            continue
        elif line.startswith("#"):
            cat = line.replace("#", "").strip()
            if cat:
                current_cat = cat
            continue

    return categories

def write_horizontal(categories, f):
    for cat in sorted(categories.keys()):
        chans = sorted(categories[cat])
        if chans:
            line = f"{cat} → " + " | ".join(chans)
            f.write(line + "\n\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        log("错误：未找到 data.txt")
        exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    if not urls:
        log("错误：data.txt 中无有效链接")
        exit(1)

    all_cats = defaultdict(set)
    total_channels = 0

    for url in urls:
        log(f"正在下载: {url}")
        content = download_m3u(url)
        if not content:
            continue

        raw_cats = parse_m3u_raw(content)
        chan_count = 0

        for cat, chans in raw_cats.items():
            all_cats[cat].update(chans)
            chan_count += len(chans)

        total_channels += chan_count
        log(f"解析到 {chan_count} 个频道")

    log(f"总计去重后：{len([ch for chans in all_cats.values() for ch in chans])} 个频道")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_horizontal(all_cats, f)

    log(f"完成！结果写入: {OUTPUT_FILE}")
