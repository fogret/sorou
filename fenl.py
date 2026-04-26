# -*- coding: utf-8 -*-
# 不跳、不绕、不改动任何东西
# 完全保持原始分组、原始顺序、不去改名字

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
    except:
        log(f"下载失败：{url}")
        return ""

def parse_original_groups(content):
    """
    纯提取原始分组，完全不改分组名、不改顺序
    只抓 #EXTGRP 与 #EXTINF → 频道名
    """
    groups = OrderedDict()
    current_group = None
    name = None

    lines = [l.strip() for l in content.splitlines() if l.strip()]

    for line in lines:
        if line.startswith("#EXTGRP:"):
            current_group = line[8:].strip()
            if current_group not in groups:
                groups[current_group] = []
            continue

        if line.startswith("#EXTINF:"):
            m = re.search(r',(.+)', line)
            if m:
                name = m.group(1).strip()
            continue

        if current_group and name and line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            # 只保存频道名，不保存地址
            groups[current_group].append(name)
            name = None

    return groups

def dedup_list(lst):
    seen = set()
    result = []
    for x in lst:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result

def write_original_format(groups, out_path):
    """
    完全按原始分组格式写入
    分组名
    频道名1 | 频道名2 | ...
    保持原始顺序
    """
    with open(out_path, "w", encoding="utf-8") as f:
        for group, chans in groups.items():
            chans = dedup_list(chans)
            if chans:
                f.write(f"{group}\n")
                f.write(" | ".join(chans) + "\n\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        log("错误：未找到 data.txt")
        exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    if not urls:
        log("错误：data.txt 中无有效链接")
        exit(1)

    all_groups = OrderedDict()

    for url in urls:
        log(f"正在处理：{url}")
        content = download(url)
        if not content:
            continue

        raw = parse_original_groups(content)

        for g, chans in raw.items():
            if g not in all_groups:
                all_groups[g] = []
            all_groups[g].extend(chans)

    total = 0
    for g in all_groups:
        all_groups[g] = dedup_list(all_groups[g])
        total += len(all_groups[g])

    log(f"总计去重后：{total} 个频道")
    write_original_format(all_groups, OUTPUT_FILE)
    log(f"完成！结果写入：{OUTPUT_FILE}")
