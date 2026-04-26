import re
import os
import time
import requests
from collections import OrderedDict

INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 分类存储
result = OrderedDict()
result["央视频道"] = set()
result["卫视频道"] = set()
result["付费频道"] = set()
result["IPTV频道"] = set()

# 匹配正则
pattern = re.compile(r'group-title="([^"]+)",([^ \n\r]+)', re.I)

# 特殊央视付费频道，强制归为央视
special_cctv = {
    "CCTV世界地理", "CCTV兵器科技", "CCTV女性时尚", "CCTV怀旧剧场",
    "CCTV电视指南", "CCTV第一剧场", "CCTV风云剧场", "CCTV风云足球",
    "CCTV风云音乐", "CCTV高尔夫网球"
}

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def clean_province(name):
    s = re.sub(r'电信|移动|联通|组播|\d+', '', name.strip())
    m = re.match(r'[\u4e00-\u9fa5]+', s)
    if m:
        return f"{m.group()}频道"
    return s

def is_cctv(name):
    if name in special_cctv:
        return True
    return name.startswith("CCTV-") or "央视" in name

def is_weishi(name):
    return "卫视" in name

def is_pay(name):
    # 已经归到央视的，不再算付费
    if name in special_cctv:
        return False
    pay_keys = ["付费", "精品", "高清", "4K", "购物", "测试", "导视", "VIP", "尊享", "数字"]
    return any(k in name for k in pay_keys)

def is_iptv(name):
    return "IPTV" in name

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

                # 依次归类
                if is_cctv(chn_name):
                    result["央视频道"].add(chn_name)
                elif is_weishi(chn_name):
                    result["卫视频道"].add(chn_name)
                elif is_pay(chn_name):
                    result["付费频道"].add(chn_name)
                elif is_iptv(chn_name):
                    result["IPTV频道"].add(chn_name)
                else:
                    prov = clean_province(group_name)
                    if prov not in result:
                        result[prov] = set()
                    result[prov].add(chn_name)

        except Exception as e:
            log(f"失败: {str(e)}")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for cat, chns in result.items():
            if not chns:
                continue
            f.write(f"{cat}\n")
            for name in sorted(chns):
                f.write(f"  {name}\n")
            f.write("\n")

    log("✅ 完成：央视+卫视+付费+IPTV + 省份频道，全部去重")

if __name__ == "__main__":
    main()
