# -*- coding: utf-8 -*-
import re
import requests

# 超时设置，避免太慢
TIMEOUT = 5

# 读取地址列表
with open("data.txt", "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

m3u = ["#EXTM3U"]

# 匹配 URL 中的数字
pattern = re.compile(r"play/(\d+)\.m3u8")

for url in lines:
    try:
        # 尝试读取 m3u8 获取频道名
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        m3u8_content = resp.text

        # 从 EXTINF 里提取频道名
        name_match = re.search(r'#EXTINF[^,]*,(.*)', m3u8_content, re.I)
        if name_match:
            name = name_match.group(1).strip()
        else:
            name = f"频道_{pattern.search(url).group(1)}"

    except:
        # 读取失败就用数字当名字
        num = pattern.search(url).group(1) if pattern.search(url) else "未知"
        name = f"频道_{num}"

    m3u.append(f"#EXTINF:-1,{name}")
    m3u.append(url)

# 输出
with open("output.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))

print("✅ 自动识别频道名完成，已生成 output.m3u")
