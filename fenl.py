# -*- coding: utf-8 -*-
"""
完全保持你原始 M3U 的分组标题
直接读取 → 原样提取 → 去重 → 输出
不改名、不推断、不换顺序
"""

import os
import re

def main():
    # 你指定的输入文件
    input_file = "data.txt"
    output_file = "fenl_output.txt"

    if not os.path.exists(input_file):
        print("[错误] 未找到 data.txt")
        exit(1)

    # 读取所有 URL
    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().startswith("http")]

    if not urls:
        print("[错误] data.txt 中无有效链接")
        exit(1)

    result = []
    group_title = None
    title = None

    for url in urls:
        print(f"[正在处理] {url}")
        content = download_m3u(url)
        if not content:
            continue

        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别分组
            if line.startswith("#EXTINF:"):
                m = re.search(r'group-title="([^"]+)"', line)
                if m:
                    group_title = m.group(1)
                continue

            # 识别频道名
            if line.startswith(("http://", "https://", "rtp://", "rtmp://")):
                if group_title:
                    result.append(f"{group_title}")
                group_title = None
                continue

    # 去重并保持顺序
    final = []
    seen = set()
    for x in result:
        if x not in seen:
            seen.add(x)
            final.append(x)

    # 写入
    with open(output_file, "w", encoding="utf-8") as f:
        for line in final:
            f.write(line + "\n")

    print(f"\n完成！已写入 {output_file}")

def download_m3u(url):
    try:
        import requests
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[下载失败] {url} → {str(e)}")
        return ""

if __name__ == "__main__":
    main()
