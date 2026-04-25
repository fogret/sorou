# -*- coding: utf-8 -*-
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== 核心配置 =====================
# 最优省份：浙江电信（源最多、最稳、高清多）
PROVINCE = "浙江电信"

# 黄金网段（浙江电信最容易出 udpxy）
IPS = [
    "61.164.99.1-20:80",
    "115.220.0.1-20:80",
    "122.228.199.1-20:80",
    "117.136.0.1-20:80",
    "223.151.0.1-20:80",
]

THREADS = 64    # GitHub 安全上限，不触发限流
TIMEOUT = 2.5

# ===================== 工具函数 =====================
def expand_ip(ip_str):
    ips = []
    match = re.match(r'(\d+\.\d+\.\d+)\.(\d+)-(\d+):(\d+)', ip_str)
    if not match:
        return ips
    pre, s, e, port = match.groups()
    for i in range(int(s), int(e)+1):
        ips.append(f"{pre}.{i}:{port}")
    return ips

def check_udpxy(host_port):
    try:
        host, port = host_port.split(':')
    except:
        return None

    for path in ['/stat', '/status']:
        url = f"http://{host_port}{path}"
        try:
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=False)
            if r.status_code in (200, 302):
                if any(k in r.text for k in ("udpxy", "Multi stream daemon", "status", "client")):
                    print(f"[有效] {url}")
                    return host_port
        except:
            continue
    return None

# ===================== 主扫描 =====================
def scan():
    print(f"===== 开始扫描 {PROVINCE} udpxy =====")
    targets = []
    for ip in IPS:
        targets += expand_ip(ip)

    valid = []
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        futs = {pool.submit(check_udpxy, t): t for t in targets}
        for f in as_completed(futs):
            res = f.result()
            if res:
                valid.append(res)

    valid = sorted(list(set(valid)))
    print(f"\n扫描完成，有效 udpxy：{len(valid)} 个")

    os.makedirs("ip", exist_ok=True)
    with open(f"ip/{PROVINCE}_ip.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid))

    print(f"已保存到 ip/{PROVINCE}_ip.txt")
    return valid

if __name__ == "__main__":
    scan()
