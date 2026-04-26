import re
import os
import time
import requests
from collections import OrderedDict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

province_channels = OrderedDict()
pattern = re.compile(r'group-title="([^"]+)",([^ \n\r]+)', re.I)

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def clean_province(name):
    # 去掉电信、移动、联通、组播等字样
    s = re.sub(r'电信|移动|联通|组播|\d+', '', name.strip())
    # 提取纯省份文字
    m = re.match(r'[\u4e00-\u9fa5]+', s)
    if m:
        return f"{m.group()}频道"
    return s

def main():
    if not os.exists(INPUT_FILE):
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

            for group_name, chn_name in matches:
                chn_name = chn_name.strip()
                if chn_name.startswith("http"):
                    continue

                province = clean_province(group_name)
                if province not in province_channels:
                    province_channels[province] = set()
                province_channels[province].add(chn_name)

        except Exception as e:
            log(f"失败: {str(e)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for province, chns in province_channels.items():
            f.write(f"{province}\n")
            for name in sorted(chns):
                f.write(f"  {name}\n")
            f.write("\n")

    log("✅ 完成：已去掉运营商 + 加频道二字 + 全局去重")

if __name__ == "__main__":
    main()
