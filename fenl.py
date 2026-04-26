import re
import os
import time
import requests
from collections import OrderedDict

# 配置
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 存储分类与频道名
groups = OrderedDict()

# 精准匹配 group-title 和频道名
pattern = re.compile(r'#EXTINF:-1\s+group-title="([^"]+)",([^ ]+)', re.IGNORECASE)

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def main():
    if not os.path.exists(INPUT_FILE):
        log(f"错误：未找到 {INPUT_FILE}")
        return

    # 读取数据源地址
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]

    log(f"读取到 {len(urls)} 个数据源")

    # 逐个解析
    total_count = 0
    for idx, url in enumerate(urls, 1):
        log(f"[{idx}/{len(urls)}] 正在解析：{url}")
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            matches = pattern.findall(resp.text)

            for group_title, channel_name in matches:
                group = group_title.strip()
                name = channel_name.strip()
                if group not in groups:
                    groups[group] = set()
                groups[group].add(name)

            count = len(matches)
            total_count += count
            log(f"   └─ 解析到 {count} 个频道")
        except Exception as e:
            log(f"   └─ 解析失败：{str(e)}")

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for group_name, channel_set in groups.items():
            f.write(f"{group_name}\n")
            for chn in sorted(channel_set):
                f.write(f"  {chn}\n")
            f.write("\n")

    log("=" * 60)
    log(f"✅ 解析完成，总计去重频道：{total_count} 个")
    log(f"✅ 结果已保存至：{OUTPUT_FILE}")
    log("=" * 60)

if __name__ == "__main__":
    main()
