import re
import os
import time
import requests
from collections import OrderedDict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 分类顺序固定
result = OrderedDict()
result["央视频道"] = set()
result["卫视频道"] = set()
result["数字频道"] = set()
result["电影频道"] = set()
result["付费频道"] = set()
result["IPTV频道"] = set()
result["华数频道"] = set()
result["BesTV&iHOT频道"] = set()

# 匹配正则
pattern = re.compile(r'group-title="([^"]+)",([^ \n\r]+)', re.I)

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def clean_province(name):
    s = re.sub(r'电信|移动|联通|组播|\d+', '', name.strip())
    m = re.match(r'[\u4e00-\u9fa5]+', s)
    return f"{m.group()}频道" if m else s

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

                # 优先级归类
                if "卫视" in chn_name:
                    result["卫视频道"].add(chn_name)
                elif chn_name.startswith("CCTV"):
                    result["央视频道"].add(chn_name)
                # 数字频道：CETV / CGTN / 卡酷 / 嘉佳 / 卡通 / 炫动 / 电视
                elif (
                    chn_name.startswith(("CETV", "CGTN"))
                    or any(k in chn_name for k in ["卡酷", "嘉佳", "卡通", "炫动", "电视"])
                ):
                    result["数字频道"].add(chn_name)
                elif "CHC" in chn_name or "电影" in chn_name:
                    result["电影频道"].add(chn_name)
                elif "华数" in chn_name:
                    result["华数频道"].add(chn_name)
                elif "BesTV" in chn_name or "iHOT" in chn_name:
                    result["BesTV&iHOT频道"].add(chn_name)
                elif "IPTV" in chn_name:
                    result["IPTV频道"].add(chn_name)
                elif any(k in chn_name for k in ["付费", "4K", "高清", "购物", "VIP"]):
                    result["付费频道"].add(chn_name)
                else:
                    if "上海" in chn_name:
                        prov = "上海频道"
                    else:
                        prov = clean_province(group_name)
                    if prov not in result:
                        result[prov] = set()
                    result[prov].add(chn_name)

        except Exception as e:
            log(f"失败: {str(e)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for cat, chns in result.items():
            if not chns:
                continue
            f.write(f"{cat}\n")
            for name in sorted(chns):
                f.write(f"  {name}\n")
            f.write("\n")

    log("✅ 全部归类完成！")

if __name__ == "__main__":
    main()
