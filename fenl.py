# -*- coding: utf-8 -*-
import os
import re
import requests
from collections import OrderedDict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

def log(msg):
    print(f"[INFO] {msg}")

def download(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log(f"下载失败：{url}")
        return ""

def parse_m3u_correctly(content):
    """
    完全按你源的 group-title="xxx" 提取分组
    并正确对应频道名
    """
    groups = OrderedDict()
    current_group = None
    current_title = None

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    for line in lines:
        # 1. 识别 group-title 分组
        if line.startswith("#EXTINF:"):
            m = re.search(r'group-title="([^"]+)"', line)
            if m:
                current_group = m.group(1)
                continue

        # 2. 识别频道名
        if line.startswith("#EXTINF:"):
            title_match = re.search(r',(.+)', line)
            if title_match:
                current_title = title_match.group(1).strip()
            continue

        # 3. 遇到播放地址 → 保存分组+频道
        if current_group and current_title and line.startswith(
            ("http://", "https://", "rtp://", "rtmp://", "udp://")
        ):
            if current_group not in groups:
                groups[current_group] = []
            groups[current_group].append(current_title)
            current_title = None  # 重置

    return groups

def dedup(lst):
    seen = set()
    res = []
    for x in lst:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res

def write_result(groups):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for group, chans in groups.items():
            chans = dedup(chans)
            if chans:
                f.write(f"{group}\n")
                f.write(" | ".join(chans) + "\n\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        log("错误：未找到 data.txt")
        exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().startswith("http")]

    if not urls:
        log("错误：data.txt 无有效链接")
        exit(1)

    all_groups = OrderedDict()

    for url in urls:
        log(f"正在处理：{url}")
        content = download(url)
        if not content:
            continue

        parsed = parse_m3u_correctly(content)

        for g, chans in parsed.items():
            if g not in all_groups:
                all_groups[g] = []
            all_groups[g].extend(chans)

    # 去重
    for g in all_groups:
        all_groups[g] = dedup(all_groups[g])

    total = sum(len(chans) for chans in all_groups.values())
    log(f"总计提取到 {total} 个频道")

    write_result(all_groups)
    log(f"完成！写入：{OUTPUT_FILE}")
