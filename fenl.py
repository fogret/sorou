# -*- coding: utf-8 -*-
import os
import re
import requests
from collections import defaultdict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 每行最多显示多少个频道（自动换行规则）
MAX_CHANNELS_PER_LINE = 10

def log(msg):
    print(f"[INFO] {msg}")

def download_m3u(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log(f"下载失败：{url} → {str(e)}")
        return ""

def parse_m3u(content):
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    cats = defaultdict(set)
    current_name = None

    for line in lines:
        if line.startswith("#EXTINF"):
            m = re.search(r',(.+)', line)
            if m:
                current_name = m.group(1).strip()
            continue

        if current_name and line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            cat = auto_classify(current_name)
            cats[cat].add(current_name)
            current_name = None

    return cats

def auto_classify(name):
    name = name.lower()
    if re.search(r"央视|cctv", name):
        return "央视频道"
    elif "卫视" in name:
        return "卫视频道"
    elif "电影" in name:
        return "电影频道"
    elif re.search(r"付费|hd|高清", name):
        return "付费频道"
    elif re.search(r"数字|tv|频道", name):
        return "数字频道"
    else:
        return "地方频道"

def write_horizontal_auto_wrap(categories, f):
    """横向排列 + 真正自动换行（每 MAX_CHANNELS_PER_LINE 换一行）"""
    for cat in sorted(categories.keys()):
        chans = sorted(categories[cat])
        if not chans:
            continue

        f.write(f"{cat} →\n")

        # 自动换行逻辑
        for i in range(0, len(chans), MAX_CHANNELS_PER_LINE):
            chunk = chans[i:i+MAX_CHANNELS_PER_LINE]
            line = " | ".join(chunk)
            f.write("  " + line + "\n")

        f.write("\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        log("错误：未找到 data.txt")
        exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    if not urls:
        log("错误：data.txt 无有效链接")
        exit(1)

    all_cats = defaultdict(set)

    for url in urls:
        log(f"正在下载: {url}")
        content = download_m3u(url)
        if not content:
            continue

        cats = parse_m3u(content)
        total = 0

        for c, chans in cats.items():
            all_cats[c].update(chans)
            total += len(chans)

        log(f"解析到 {total} 个频道")

    total_final = len([ch for chans in all_cats.values() for ch in chans])
    log(f"总计去重后：{total_final} 个频道")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        write_horizontal_auto_wrap(all_cats, f)

    log(f"完成！写入: {OUTPUT_FILE}")
