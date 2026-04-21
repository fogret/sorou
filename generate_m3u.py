# -*- coding: utf-8 -*-
import re

INPUT_PATH = "/data.txt"
OUTPUT_PATH = "output.m3u"

# 匹配频道名 + URL（通用 IPTV 格式）
pattern = re.compile(r'^(.*?)(https?://.+)', re.MULTILINE)

seen = set()
lines_out = ['#EXTM3U']

with open(INPUT_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

matches = pattern.findall(content)

for name_part, url in matches:
    url = url.strip()
    if url in seen:
        continue
    seen.add(url)

    name = name_part.strip()
    if not name:
        name = "未知频道"

    lines_out.append(f'#EXTINF:-1,{name}')
    lines_out.append(url)

# 写入 m3u
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines_out))

print(f"处理完成，共 {len(seen)} 个频道，已生成 {OUTPUT_PATH}")
