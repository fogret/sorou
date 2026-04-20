# -*- coding: utf-8 -*-
import re

# 读取 data.txt
with open("data.txt", "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

# 只输出标准 m3u，不瞎改名
m3u = ["#EXTM3U"]

for line in lines:
    # 提取 URL
    urls = re.findall(r'https?://\S+', line)
    if not urls:
        continue
    url = urls[0]

    # 标准格式：只写 EXTINF + URL，不折腾名字
    m3u.append("#EXTINF:-1,")
    m3u.append(url)

# 写入
with open("output.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))
