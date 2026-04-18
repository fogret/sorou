import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/fogret/sourt/master/config/subscribe.txt"
OUT_TXT = "channels.txt"
OUT_M3U = "channels.m3u"
LOG_FILE = "process.log"

def log(msg):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{dt}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fetch_text(url):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.text
    except:
        return ""

def is_media_url(url):
    # 只保留真正的直播流，排除订阅文件
    if not url.startswith("http"):
        return False
    if any(x in url.lower() for x in [".m3u", ".txt", "subscribe", "list", "index.php"]):
        return False
    return True

def parse_line(line):
    line = line.strip()
    if not line:
        return None

    if "," in line:
        name_part, _, url = line.rpartition(",")
        name = name_part.strip()
        url = url.strip()
        if name and is_media_url(url):
            return (name, url)
    return None

def main():
    log("===== 任务开始 =====")
    log(f"下载主订阅：{SOURCE_URL}")

    main_text = fetch_text(SOURCE_URL)
    if not main_text:
        log("主订阅下载失败")
        return

    # 收集子订阅
    sub_urls = []
    for line in main_text.splitlines():
        line = line.strip()
        if line.startswith("http") and ".txt" in line or ".m3u" in line:
            sub_urls.append(line)

    log(f"找到子订阅：{len(sub_urls)} 个")

    all_channels = []
    seen = set()

    for i, sub in enumerate(sub_urls, 1):
        log(f"[{i}/{len(sub_urls)}] 解析 {sub[:60]}")
        text = fetch_text(sub)
        if not text:
            continue

        for line in text.splitlines():
            ch = parse_line(line)
            if ch:
                name, url = ch
                if url not in seen:
                    seen.add(url)
                    all_channels.append((name, url))

    log(f"解析完成，去重后有效频道：{len(all_channels)} 个")

    # 输出
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for name, url in all_channels:
            f.write(f"{name},{url}\n")

    with open(OUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in all_channels:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")

    log("全部完成！已生成 channels.txt + channels.m3u")
    log("===== 任务结束 =====\n")

if __name__ == "__main__":
    main()
