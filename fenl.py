import re
import os
import time
import requests
from collections import OrderedDict

# ===================== 配置 =====================
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
TIMEOUT = 20

# 存储结构：分类 -> {url: (名称, url)}
categories = OrderedDict()
total_channels = 0
total_urls = 0

# 正则（兼容各种格式）
genre_re = re.compile(r'^\s*([^,#]+)\s*,\s*#genre#', re.IGNORECASE)
channel_re = re.compile(r'^\s*([^,#]+?)\s*,\s*(https?://\S+)', re.IGNORECASE)

def log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def parse_text(content):
    global total_channels
    current_genre = "未分类频道"
    count = 0

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 匹配分类
        g_match = genre_re.search(line)
        if g_match:
            current_genre = g_match.group(1).strip()
            if current_genre not in categories:
                categories[current_genre] = OrderedDict()
            continue

        # 匹配频道
        c_match = channel_re.search(line)
        if c_match:
            name = c_match.group(1).strip()
            url = c_match.group(2).strip()

            if current_genre not in categories:
                categories[current_genre] = OrderedDict()

            # 按URL去重
            if url not in categories[current_genre]:
                categories[current_genre][url] = (name, url)
                total_channels += 1
                count += 1
    return count

def main():
    global total_urls
    log("=" * 60)
    log("开始解析数据源：" + INPUT_FILE)
    log("=" * 60)

    if not os.path.exists(INPUT_FILE):
        log(f"❌ 错误：未找到文件 {INPUT_FILE}")
        return

    # 读取所有源地址
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        raw_urls = [line.strip() for line in f if line.strip()]

    log(f"✅ 读取到 {len(raw_urls)} 个数据源地址")

    # 逐个解析
    for idx, url in enumerate(raw_urls, 1):
        log(f"[{idx}/{len(raw_urls)}] 正在解析：{url}")
        try:
            resp = requests.get(
                url,
                timeout=TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            resp.raise_for_status()
            cnt = parse_text(resp.text)
            log(f"   └─ 成功解析到 {cnt} 个频道")
        except Exception as e:
            log(f"   └─ 解析失败：{str(e)}")

    log("=" * 60)
    log(f"📊 解析完成：总计去重后频道数量 = {total_channels} 个")
    log(f"📂 正在写入文件：{OUTPUT_FILE}")

    # 写入结果
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for genre, items in categories.items():
            f.write(f"{genre},#genre#\n")
            for name, url in items.values():
                f.write(f"{name},{url}\n")
            f.write("\n")

    log("✅ 全部完成！文件已生成")
    log("=" * 60)

if __name__ == "__main__":
    main()
