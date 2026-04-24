import requests
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Authorization": f"token {os.getenv('GH_TOKEN')}"
}

QUERIES = [
    "udpxy rtp",
    "iptv rtp 239",
    "IPTV 组播",
    "rtp://239",
    "/rtp/239"
]

# 精准匹配你要的格式
RTP_PATTERN = re.compile(
    r"https?://[0-9A-Za-z\.-]+:\d+/rtp/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",
    re.I
)

result = set()

def fetch_raw(raw_url):
    try:
        r = requests.get(raw_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return RTP_PATTERN.findall(r.text)
    except:
        return []
    return []

def search_code(q):
    try:
        url = f"https://api.github.com/search/code?q={requests.utils.quote(q)}+extension:txt+extension:m3u"
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        return [item["html_url"].replace("/blob/", "/raw/") for item in res.get("items", [])]
    except:
        return []

if __name__ == "__main__":
    print("=" * 60)
    print("      GitHub 组播源扫描器（带Token版）")
    print("=" * 60)

    all_raw = []
    for q in QUERIES:
        print(f"搜索: {q}")
        all_raw.extend(search_code(q))
        time.sleep(2)

    print(f"\n找到文件: {len(all_raw)}")

    with ThreadPoolExecutor(10) as e:
        for urls in e.map(fetch_raw, all_raw):
            for u in urls:
                result.add(u.strip())

    out = sorted(result)
    with open("multicast_iptv.txt", "w", encoding="utf-8") as f:
        f.write(f"# 扫描时间: {time.ctime()}\n")
        f.write(f"# 有效组播源: {len(out)}\n\n")
        f.write("\n".join(out))

    print(f"\n完成！有效组播源：{len(out)}")
