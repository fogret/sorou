# -*- coding: utf-8 -*-
import os
import requests

# 配置
subscribe_url = "https://raw.githubusercontent.com/fogret/sourt/master/config/subscribe.txt"
target_ip = "43.251.226.110"
tmp_dir = "./tmp_subs"

def main():
    os.makedirs(tmp_dir, exist_ok=True)

    # 1. 下载主订阅列表
    try:
        print("正在下载订阅列表...")
        resp = requests.get(subscribe_url, timeout=15)
        resp.raise_for_status()
        lines = resp.text.splitlines()
    except Exception as e:
        print("下载订阅列表失败:", e)
        return

    # 提取所有源地址
    sources = [
        line.strip()
        for line in lines
        if line.strip() and line.strip().endswith((".m3u", ".m3u8", ".txt"))
    ]

    print(f"共获取 {len(sources)} 个源")

    found = []

    # 2. 逐个下载 + 本地扫描
    for idx, url in enumerate(sources, 1):
        try:
            print(f"[{idx}/{len(sources)}] 下载: {url}")
            res = requests.get(url, timeout=12)
            content = res.text

            # 本地检查IP
            if target_ip in content:
                print("✅ 找到目标IP")
                found.append(url)

        except Exception as e:
            print(f"❌ 下载/扫描失败: {str(e)[:60]}")

    # 3. 结果
    print("\n===== 扫描完成 =====")
    if found:
        print("\n包含 IP %s 的源：" % target_ip)
        for u in found:
            print(u)
    else:
        print("未找到包含该IP的源")

if __name__ == "__main__":
    main()
