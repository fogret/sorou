import re
import os
import time
import requests
from collections import OrderedDict

# ===================== 配置 =====================
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
TIMEOUT = 20

categories = OrderedDict()
total_channels = 0

# 精准匹配你这种格式
pattern = re.compile(
    r'#EXTINF:-1\s+group-title="([^"]+)",([^ ]+)\s+(https?://\S+)',
    re.IGNORECASE
)

def log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def parse_content(text):
    global total_channels
    count = 0
    matches = pattern.findall(text)

    for group, name, url in matches:
        group = group.strip()
        name = name.strip()
        url = url.strip()

        if group not in categories:
            categories[group] = OrderedDict()
        if url not in categories[group]:
            categories[group][url] = (name, url)
            total_channels += 1
            count += 1
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
