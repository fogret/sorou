# channel_ai.py
# 适配OK影视安卓4.0专用版，生成标准M3U（含频道名）
import requests
import json
import time

def main():
    print("="*50)
    print(f"📅 开始运行：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("📶 适配OK影视安卓4.0专用版接口")
    print("="*50)

    # OK影视4.0专版常用接口（选一个即可）
    api_urls = [
        "https://cnb.cool/xiaomideyun/xiaomideyun/-/git/raw/main/mi.json",
        "https://ghproxy.com/https://raw.githubusercontent.com/yyds765/uzvideo/main/box.json",
        "https://ghproxy.cn/https://raw.githubusercontent.com/fenfa9988/iptv/main/itvbox.txt"
    ]

    channels = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for idx, url in enumerate(api_urls, 1):
        try:
            print(f"🔗 尝试接口 {idx}/{len(api_urls)}: {url}")
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            content = resp.text.strip()

            # 尝试解析JSON（兼容OK影视加密/明文混合）
            try:
                data = json.loads(content)
                # 提取频道（适配OK影视常见结构）
                if isinstance(data, list):
                    for item in data:
                        if "name" in item and "url" in item:
                            channels.append({"name": item["name"], "url": item["url"]})
                        elif "title" in item and "link" in item:
                            channels.append({"name": item["title"], "url": item["link"]})
                elif isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, dict) and ("url" in v or "link" in v):
                            name = v.get("name", v.get("title", k))
                            url = v.get("url", v.get("link", ""))
                            if url:
                                channels.append({"name": name, "url": url})
            except json.JSONDecodeError:
                # 非JSON，按行提取（适配OK影视txt接口）
                lines = content.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith(("http://", "https://", "rtmp://", "rtsp://")):
                        channels.append({"name": f"OK频道_{len(channels)+1}", "url": line})

            print(f"✅ 接口 {idx} 处理完成，当前累计频道：{len(channels)}")

        except Exception as e:
            print(f"⚠️ 接口 {idx} 失败: {str(e)[:60]}...")
            continue

    # 去重
    seen = set()
    unique_channels = []
    for ch in channels:
        if ch["url"] not in seen:
            seen.add(ch["url"])
            unique_channels.append(ch)

    # 生成M3U
    m3u = ["#EXTM3U"]
    for ch in unique_channels:
        m3u.append(f'#EXTINF:-1,{ch["name"]}')
        m3u.append(ch["url"])

    # 写入文件
    with open("channels.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    print("="*50)
    print(f"✅ 生成完成：共 {len(unique_channels)} 个频道")
    print(f"📄 输出文件：channels.m3u")
    print("="*50)

if __name__ == "__main__":
    main()
