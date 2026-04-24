import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor

# ===================== 配置 =====================
# 搜索页面（国内可访问）
SEARCH_PAGES = [
    "https://github.com/search?q=iptv+rtp+239&type=Code",
    "https://github.com/search?q=udpxy+iptv&type=Code",
    "https://github.com/search?q=组播源+rtp&type=Code",
    "https://github.com/search?q=电信组播+rtp&type=Code",
    "https://github.com/search?q=multicast+rtp+iptv&type=Code"
]

# 匹配规则：只抓你要的格式
RTP_PATTERN = re.compile(r'https?://[^\s"<>]+/rtp/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', re.I)
# 只处理 txt/m3u
FILTER_EXT = (".txt", ".m3u", ".m3u8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

result = set()

# ===================== 爬取函数 =====================
def fetch_raw(url):
    try:
        raw_url = url.replace("/blob/", "/raw/")
        r = requests.get(raw_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return RTP_PATTERN.findall(r.text)
    except:
        return []
    return []

def scan_page(search_url):
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        # 提取所有代码文件链接
        links = re.findall(r'href="(/[^/]+/[^/]+/blob/[^"]+)"', r.text)
        valid = []
        for l in links:
            if any(l.endswith(e) for e in FILTER_EXT):
                valid.append("https://github.com" + l)
        return valid
    except:
        return []

# ===================== 主程序 =====================
if __name__ == "__main__":
    print("=" * 60)
    print("      GitHub 组播源扫描器（仅提取 /rtp/ 格式）")
    print("=" * 60)

    all_files = []
    for page in SEARCH_PAGES:
        print(f"正在搜索: {page}")
        files = scan_page(page)
        all_files.extend(files)
        time.sleep(1)

    print(f"\n找到 {len(all_files)} 个源文件，开始提取...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        for urls in executor.map(fetch_raw, all_files):
            for u in urls:
                result.add(u.strip())

    # 保存
    sorted_result = sorted(result)
    with open("multicast_iptv.txt", "w", encoding="utf-8") as f:
        f.write(f"# 扫描完成 {time.ctime()}\n")
        f.write(f"# 共 {len(sorted_result)} 个高质量组播源\n\n")
        for line in sorted_result:
            f.write(line + "\n")

    print(f"\n✅ 完成！共抓取 {len(sorted_result)} 个组播源")
    print("📄 已保存到: multicast_iptv.txt")
