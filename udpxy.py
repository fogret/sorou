# -*- coding: utf-8 -*-
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== 核心配置 =====================
PROVINCE = "浙江电信"

# 更容易出有效 udpxy 的热门网段 + 常用端口
IPS = [
    "115.220.30.1-50:8080",
    "115.220.31.1-50:8080",
    "122.228.198.1-30:8080",
    "61.164.98.1-30:8090",
    "61.164.99.1-30:8888",
    "117.136.40.1-30:8080",
    "223.150.40.1-30:8080",
]

THREADS = 64
TIMEOUT = 3

# ===================== 工具函数 =====================
def expand_ip(ip_str):
    ips = []
    match = re.match(r'(\d+\.\d+\.\d+)\.(\d+)-(\d+):(\d+)', ip_str)
    if not match:
        print(f"[调试] 网段格式错误: {ip_str}")
        return ips
    pre, s, e, port = match.groups()
    for i in range(int(s), int(e)+1):
        ip_port = f"{pre}.{i}:{port}"
        ips.append(ip_port)
    print(f"[调试] 展开网段 {ip_str} -> {len(ips)} 个目标")
    return ips

def check_udpxy(host_port):
    print(f"[调试] 正在检测: {host_port}")
    
    try:
        host, port = host_port.split(':')
    except Exception as e:
        return None

    for path in ['/stat', '/status', '/']:
        url = f"http://{host_port}{path}"
        try:
            r = requests.get(
                url,
                timeout=TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"},
                allow_redirects=False
            )
            if r.status_code == 200:
                if any(k in r.text for k in ("udpxy", "Multi stream", "client", "stat")):
                    print(f"[✅ 有效] {host_port}")
                    return host_port
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass
    print(f"[❌ 无效] {host_port}")
    return None

# ===================== 主扫描 =====================
def scan():
    print(f"===== 开始扫描 {PROVINCE} udpxy =====")
    targets = []
    for ip in IPS:
        targets += expand_ip(ip)

    print(f"[调试] 总待扫描目标: {len(targets)} 个")
    valid = []

    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        futs = {pool.submit(check_udpxy, t): t for t in targets}
        for idx, f in enumerate(as_completed(futs), 1):
            res = f.result()
            if res:
                valid.append(res)
            if idx % 20 == 0:
                print(f"[调试] 已完成 {idx}/{len(targets)}，有效: {len(valid)}")

    valid = sorted(list(set(valid)))
    print(f"\n===== 扫描完成 =====")
    print(f"[结果] 有效 udpxy: {len(valid)}")
    print(f"[结果] {valid}")

    os.makedirs("ip", exist_ok=True)
    out_path = f"ip/{PROVINCE}_ip.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(valid))

    print(f"[调试] 已保存到: {out_path}")
    return valid

if __name__ == "__main__":
    scan()
