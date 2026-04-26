import re
import os
import time
import requests
from collections import OrderedDict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

groups = OrderedDict()
# 只匹配分类和频道名，自动忽略链接
pattern = re.compile(r'group-title="([^"]+)",([^ \n\r]+)', re.I)

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def main():
    if not os.path.exists(INPUT_FILE):
        log(f"未找到 {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip().startswith("http")]

    log(f"读取到 {len(urls)} 个数据源")

    for url in urls:
        log(f"解析: {url}")
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            matches = pattern.findall(resp.text)

            for g, name in matches:
                g = g.strip()
                name = name.strip()
                # 过滤掉链接行
                if name.startswith("http"):
                    continue
                if g not in groups:
                    groups[g] = set()
                groups[g].add(name)
        except Exception as e:
            log(f"失败: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for g, names in groups.items():
            f.write(f"{g}\n")
            for n in sorted(names):
                f.write(f"  {n}\n")
            f.write("\n")

    log("✅ 完成！已去掉所有播放地址，只保留分类和频道名")

if __name__ == "__main__":
    main()
