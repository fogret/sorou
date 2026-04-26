import re
import os
import time
import requests
from collections import OrderedDict

# 配置
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
TIMEOUT = 15

# 存储结构：分类 -> 有序频道集合（自动去重）
result = OrderedDict()

# 正则
genre_pattern = re.compile(r'^\s*([^,#]+?)\s*,#genre#\s*$')
line_pattern = re.compile(r'^\s*([^,#]+?)\s*,\s*(https?://\S+?)\s*$')

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def parse_content(text):
    current_genre = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 匹配分类
        g_match = genre_pattern.match(line)
        if g_match:
            current_genre = g_match.group(1).strip()
            if current_genre not in result:
                result[current_genre] = OrderedDict()
            continue

        # 匹配频道
        c_match = line_pattern.match(line)
        if c_match and current_genre is not None:
            name = c_match.group(1).strip()
            url = c_match.group(2).strip()
            # 用 url 去重
            result[current_genre][url] = (name, url)

def main():
    if not os.path.exists(INPUT_FILE):
        log(f"文件不存在：{INPUT_FILE}")
        return

    # 读取源链接
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        urls = [l.strip() for l in f if l.strip()]

    log(f"共 {len(urls)} 个源，开始解析")

    for url in urls:
        try:
            resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            parse_content(resp.text)
            log(f"成功：{url}")
        except Exception as e:
            log(f"失败：{url} | {str(e)}")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for genre, channels in result.items():
            f.write(f"{genre},#genre#\n")
            for name, url in channels.values():
                f.write(f"{name},{url}\n")
            f.write("\n")

    log(f"完成！已保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
