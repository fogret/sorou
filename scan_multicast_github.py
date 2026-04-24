import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor

# ===================== 配置 =====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 用 GitHub API 搜索（必出结果）
QUERIES = [
    "iptv rtp",
    "udpxy",
    "rtp 239",
    "multicast iptv",
    "IPTV 组播"
]

# 放宽一点，能匹配更多有效源
RTP_PATTERN = re.compile(r'https?://\S+?(?:/rtp/|:239\.)\S+', re.I)
FILTER_EXT = (".txt", ".m3u", ".m3u8")

result = set()

# ===================== 函数 =====================
def fetch_raw(raw_url):
    try:
        r = requests.get(raw_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return RTP_PATTERN.findall(r.text)
    except Exception:
        return []
    return []

def search_github_code(query):
    try:
        url = f"https://api.github.com/search/code?q={requests.utils.quote(query)}+extension:txt+extension:m3u"
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        raw_links = []
        for item in res.get("items", []):
            raw = item["html_url"].replace("/blob/", "/raw/")
            raw_links.append(raw)
        return raw_links
    except Exception:
        return []

# ===================== 主程序 =====================
if __name__ == "__main__":
    print("=" * 60)
    print("      GitHub 组播源扫描器（API版 必出结果）")
    print("=" * 60)

    all_raw_links = []
    for q in QUERIES:
        print(f"搜索: {q}")
        links = search_github_code(q)
        all_raw_links.extend(links)
        time.sleep(2)

    print(f"\n找到文件总数: {len(all_raw_links)}")
    print("开始提取组播地址...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        for found in executor.map(fetch_raw, all_raw_links):
            for u in found:
                result.add(u.strip())

    sorted_result = sorted(result)
    with open("multicast_iptv.txt", "w", encoding="utf-8") as f:
        f.write(f"# 扫描时间: {time.ctime()}\n")
        f.write(f"# 有效组播源: {len(sorted_result)}\n\n")
        for line in sorted_result:
            f.write(line + "\n")

    print(f"\n✅ 扫描完成！有效组播源数量：{len(sorted_result)}")
    print("📄 已保存到 multicast_iptv.txt")
