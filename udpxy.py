# -*- coding: utf-8 -*-
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 配置 ====================
PROVINCE = "全国酒店源"

# 酒店/小区/宾馆最容易出 udpxy 的网段（实测有效率极高）
IPS = [
    "113.106.52.1-100:80",
    "113.106.53.1-100:8080",
    "119.23.24.1-100:8080",
    "120.83.12.1-100:8080",
    "182.148.12.1-100:80",
    "218.75.19.1-100:8080",
    "223.113.60.1-100:80",
    "221.238.14.1-100:8080",
]

THREADS = 64
TIMEOUT = 3

# ==================== 展开IP段 ====================
def expand_ip(ip_str):
    ips = []
    match = re.match(r'(\d+\.\d+\.\d+)\.(\d+)-(\d+):(\d+)', ip_str)
    if not match:
        return ips
    pre, s, e, port = match.groups()
    for i in range(int(s), int(e)+1):
        ips.append(f"{pre}.{i}:{port}")
    return ips

# ==================== 检测 udpxy ====================
def check_udpxy(host_port):
    print(f"[检测] {host_port}")
    host, port = host_port.split(':')

    paths = ['/stat', '/status', '/udp/239.1.1.1', '/rtp/239.1.1.1']
    for path in paths:
        url = f"http://{host_port}{path}"
        try:
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=False)
            if r.status_code == 200:
                t = r.text.lower()
                if "udpxy" in t or "stream" in t or "client" in t or "multicast" in t:
                    print(f"[✅ 有效] {host_port}")
                    return host_port
        except:
            continue
    print(f"[无效] {host_port}")
    return None

# ==================== 主函数 ====================
def scan():
    targets = []
    for ip in IPS:
        targets += expand_ip(ip)
    print(f"总目标：{len(targets)}")

    valid = []
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        futures = {pool.submit(check_udpxy, t): t for t in targets}
        for f in as_completed(futures):
            res = f.result()
            if res:
                valid.append(res)

    valid = sorted(list(set(valid)))
    print("\n===== 扫描完成 =====")
    print(f"有效 udpxy：{len(valid)}")
    print(valid)

    os.makedirs("ip", exist_ok=True)
    with open("ip/酒店_ip.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid))

if __name__ == "__main__":
    scan()
