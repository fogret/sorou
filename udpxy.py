import requests
from concurrent.futures import ThreadPoolExecutor

# ===================== 已填好：贵州电信全IP段 =====================
IP_RANGES = [
    "58.42.0.0/16",
    "211.98.0.0/16",
    "219.141.0.0/16",
    "222.86.0.0/15",
    "111.123.0.0/16",
    "113.206.0.0/16",
    "183.66.0.0/16",
    "182.100.0.0/15",
    "119.131.64.0/18",
    "119.131.128.0/18",
    "117.136.0.0/15",
    "118.112.0.0/14"
]

# udpxy常见端口
PORTS = [4022, 8888, 8080, 5000, 5002, 8000, 9000, 9090, 6666, 7777]

# 验证是否为udpxy
def check_udpxy(ip, port):
    try:
        url = f"http://{ip}:{port}/status"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200 and "udpxy" in resp.text:
            print(f"[有效] {url}")
    except:
        return

# 生成IP列表（简化版，仅演示）
def generate_ips_from_range(ip_range):
    import ipaddress
    net = ipaddress.IPv4Network(ip_range, strict=False)
    return [str(ip) for ip in net.hosts()]

# 批量扫描
if __name__ == "__main__":
    print("开始扫描贵州电信 udpxy 服务器...")
    with ThreadPoolExecutor(max_workers=50) as executor:
        for ip_range in IP_RANGES:
            try:
                ips = generate_ips_from_range(ip_range)
                for ip in ips:
                    for port in PORTS:
                        executor.submit(check_udpxy, ip, port)
            except:
                continue
