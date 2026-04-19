# -*- coding: utf-8 -*-
import requests

# 目标订阅地址
subscribe_url = "https://raw.githubusercontent.com/fogret/sourt/master/config/subscribe.txt"
# 要查找的IP
target_ip = "43.251.226.110"

def main():
    try:
        print("正在获取订阅列表...")
        resp = requests.get(subscribe_url, timeout=15)
        resp.raise_for_status()
        lines = resp.text.splitlines()
    except Exception as e:
        print("获取订阅列表失败:", e)
        return

    # 提取所有以 m3u、m3u8、txt 结尾的链接
    sources = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith((".m3u", ".m3u8", ".txt")):
            sources.append(line)

    print(f"共找到 {len(sources)} 个源，开始扫描IP...\n")

    found = []
    for url in sources:
        try:
            print(f"扫描: {url}")
            res = requests.get(url, timeout=10)
            if target_ip in res.text:
                print("✅ 找到目标IP！来源:", url)
                found.append(url)
        except Exception as e:
            print(f"❌ 访问失败: {url[:50]}...")

    print("\n===== 扫描完成 =====")
    if found:
        print("包含IP " + target_ip + " 的源:")
        for u in found:
            print("-", u)
    else:
        print("未在任何订阅中找到该IP")

if __name__ == "__main__":
    main()
