import re
import os
import time
import requests
from collections import OrderedDict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 按省份分组，自动去重
province_channels = OrderedDict()

# 匹配分类与频道名
pattern = re.compile(r'group-title="([^"]+)",([^ \n\r]+)', re.I)

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_province(group_name):
    """从分类名里提取纯省份，去掉 -组播1 之类后缀"""
    # 匹配省份开头
    province_match = re.match(r'([\u4e00-\u9fa5]+)', group_name.strip())
    if province_match:
        return province_match.group(1)
    return group_name

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

            for group_name, chn_name in matches:
                chn_name = chn_name.strip()
                if chn_name.startswith("http"):
                    continue

                province = get_province(group_name)
                if province not in province_channels:
                    province_channels[province] = set()
                province_channels[province].add(chn_name)

        except Exception as e:
            log(f"失败: {e}")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for province, chns in province_channels.items():
            f.write(f"{province}\n")
            for name in sorted(chns):
                f.write(f"  {name}\n")
            f.write("\n")

    log("✅ 完成：省份分类 + 频道去重，无地址")

if __name__ == "__main__":
    main()
