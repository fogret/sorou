import requests
from datetime import datetime

# 配置
SOURCE_URL = "https://raw.githubusercontent.com/fogret/sourt/master/config/subscribe.txt"
OUT_TXT = "channels.txt"
OUT_M3U = "channels.m3u"
LOG_FILE = "process.log"

# 日志
def log(msg):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{dt}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# 获取单个文本
def fetch_text(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except:
        return ""

# 解析一行 line 得到 (name, url)
def parse_line(line):
    line = line.strip()
    if not line or "," not in line:
        return None
    name_part, _, url = line.rpartition(",")
    name = name_part.strip()
    url = url.strip()
    if url.startswith("http"):
        return (name, url)
    return None

# 主程序
def main():
    log("===== 任务开始 =====")
    log(f"下载主订阅：{SOURCE_URL}")

    main_text = fetch_text(SOURCE_URL)
    if not main_text:
        log("主订阅下载失败")
        return

    # 提取所有子订阅
    sub_urls = []
    for line in main_text.splitlines():
        line = line.strip()
        if line.startswith("http"):
            sub_urls.append(line)

    log(f"找到子订阅数量：{len(sub_urls)} 个")

    # 批量解析所有订阅
    all_channels = []
    seen_url = set()

    for idx, sub in enumerate(sub_urls, 1):
        log(f"[{idx}/{len(sub_urls)}] 解析：{sub}")
        text = fetch_text(sub)
        if not text:
            continue

        for line in text.splitlines():
            ch = parse_line(line)
            if ch:
                name, url = ch
                if url not in seen_url:
                    seen_url.add(url)
                    all_channels.append(ch)

    log(f"所有订阅解析完成，去重后总频道：{len(all_channels)} 个")

    # 写入 txt
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for name, url in all_channels:
            f.write(f"{name},{url}\n")

    # 写入 m3u
    with open(OUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in all_channels:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")

    log("全部完成！已生成 channels.txt + channels.m3u")
    log("===== 任务结束 =====\n")

if __name__ == "__main__":
    main()
