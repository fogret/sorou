import requests
import ipaddress
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ===================== 日志配置 =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("udpxy_scan.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ===================== 配置 =====================
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

PORTS = [4022, 8888, 8080, 5000, 5002, 8000, 9000, 9090, 6666, 7777]

valid_list = []

# ===================== 检测函数 =====================
def check_udpxy(ip, port):
    url = f"http://{ip}:{port}/status"
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200 and "udpxy" in r.text.lower():
            logging.info(f"有效 → {url}")
            valid_list.append(f"{ip}:{port}")
    except requests.exceptions.Timeout:
        logging.debug(f"超时 → {url}")
    except requests.exceptions.ConnectionError:
        logging.debug(f"拒绝 → {url}")
    except Exception as e:
        logging.debug(f"错误 → {url} | {str(e)}")

# ===================== IP 生成 =====================
def ip_range_to_list(cidr):
    try:
        net = ipaddress.IPv4Network(cidr, strict=False)
        return [str(ip) for ip in net.hosts()]
    except:
        logging.error(f"网段解析失败: {cidr}")
        return []

# ===================== 主扫描 =====================
if __name__ == "__main__":
    start = datetime.now()
    logging.info("=" * 50)
    logging.info("贵州电信 udpxy 批量扫描启动")
    logging.info(f"开始时间: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 50)

    with ThreadPoolExecutor(max_workers=50) as pool:
        for cidr in IP_RANGES:
            logging.info(f"正在扫描网段: {cidr}")
            ip_list = ip_range_to_list(cidr)
            for ip in ip_list:
                for port in PORTS:
                    pool.submit(check_udpxy, ip, port)

    # 结束统计
    end = datetime.now()
    cost = (end - start).total_seconds()

    logging.info("=" * 50)
    logging.info(f"扫描完成 | 耗时: {cost:.1f}s | 找到有效: {len(valid_list)} 个")
    logging.info("=" * 50)

    # 保存结果
    if valid_list:
        with open("udpxy.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(valid_list))
        logging.info("结果已保存至 udpxy.txt")
