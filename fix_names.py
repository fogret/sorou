# -*- coding: utf-8 -*-
import re

with open("data.txt", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

m3u = ["#EXTM3U"]
p = re.compile(r"play/(\d+)\.m3u8")

for line in lines:
    match = p.search(line)
    if match:
        num = match.group(1)
        m3u.append(f"#EXTINF:-1,{num}")
        m3u.append(line)

with open("output.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))
