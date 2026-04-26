import re
import os
import time
import requests
from collections import OrderedDict

# ===================== 配置 =====================
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
TIMEOUT = 20

# 存储结构
categories = OrderedDict()
total_channels = 0

# 通用正则
genre_re   = re.compile(r'^\s*([^,#]+)\s*,\s*#genre#', re.I)
channel_re = re.compile(r'^\s*([^,#]+?)\s*,\s*(https?://\S+)', re.I)
# m3u 专用
extinf_re  = re.compile(r'#EXTINF:-1,(.*)', re.I)
url_re     = re.compile(r'^(https?://\S+)', re.I)

def log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def parse_content(content):
    global total_channels
    current_genre = "默认频道"
    current_name = None
    count = 0

    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. 分类行
        g_match = genre_re.search(line)
        if g_match:
            current_genre = g_match.group(1).strip()
            if current_genre not in categories:
                categories[current_genre] = OrderedDict()
            continue

        # 2. 普通频道格式：名称,链接
        c_match = channel_re.search(line)
        if c_match:
            name = c_match.group(1).strip()
            url  = c_match.group(2).strip()
            if current_genre not in categories:
                categories[current_genre] = OrderedDict()
            if url not in categories[current_genre]:
                categories[current_genre][url] = (name, url)
                total_channels += 1
                count += 1
            continue

        # 3. m3u 格式 #EXTINF:-1,频道名
        ext_match = extinf_re.search(line)
        if ext_match:
            current_name = ext_match.group(1).strip()
            continue

        # 4. m3u 链接行
        if current_name and url_re.search(line):
            url = line.strip()
            if current_genre not in categories:
                categories[current_genre] = OrderedDict()
            if url not in categories[current_genre]:
                categories[current_genre][url] = (current_name, url)
                total_channels += 1
                count += 1
            current_name = None
            continue

    return count

def main():
    log("=" * 60)
    log("开始解析数据源：data.txt")
    log("=" * 60)

    if not os.path.exists(INPUT_FILE):
        log(f"❌ 未找到 {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        urls = [l.strip() for l in f if l.strip()]

    log(f"✅ 读取到 {len(urls)} 个数据源")

    for idx, url in enumerate(urls, 1):
        log(f"[{idx}/{len(urls)}] 解析：{url}")
        try:
            resp = requests.get(
                url,
                timeout=TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            resp.raise_for_status()
            cnt = parse_content(resp.text)
            log(f"   └─ 成功解析频道：{cnt} 个")
        except Exception as e:
            log(f"   └─ 失败：{str(e)}")

    log("=" * 60)
    log(f"📊 去重后总频道：{total_channels} 个")
    log(f"📄 写入文件：{OUTPUT_FILE}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for genre, items in categories.items():
            f.write(f"{genre},#genre#\n")
            for name, url in items.values():
                f.write(f"{name},{url}\n")
            f.write("\n")

    log("✅ 解析完成！")
    log("=" * 60)

if __name__ == "__main__":
    main()
