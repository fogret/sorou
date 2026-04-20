# -*- coding: utf-8 -*-
import re

# 读取 data.txt
with open("data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

m3u = ["#EXTM3U"]

# 匹配你的播放地址
pattern = re.compile(r"http://43\.251\.226\.110:8880/play/(\d+)\.m3u8", re.I)

for line in lines:
    line = line.strip()
    if not line:
        continue

    match = pattern.search(line)
    if not match:
        continue

    num = match.group(1)
    url = match.group(0)

    # 自动命名：频道_数字（干净不乱码）
    name = f"频道_{num}"
    m3u.append(f"#EXTINF:-1,{name}")
    m3u.append(url)

# 写入标准 m3u
with open("output.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))

print("✅ 生成 output.m3u 完成")
