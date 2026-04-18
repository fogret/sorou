# channel_ai.py
import requests
import json
import time

def main():
    print("📶 开始获取 JSON 接口...")
    json_url = "https://cnb.cool/xiaomideyun/xiaomideyun/-/git/raw/main/mi.json"
    output_m3u = "channels.m3u"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.get(json_url, headers=headers, timeout=20)
        print(f"✅ 接口请求完成，状态码: {resp.status_code}")

        data = resp.json()
        print("✅ JSON 解析成功")

        m3u_lines = ["#EXTM3U"]
        count = 0

        for category in data.get("data", {}).get("list", []):
            group = category.get("type_name", "影视").strip()
            vod_list = category.get("vod_list", [])

            for item in vod_list:
                name = item.get("title", f"频道_{count+1}")
                url = item.get("play_url", "")
                if url:
                    m3u_lines.append(f'#EXTINF:-1 group-title="{group}",{name}')
                    m3u_lines.append(url)
                    count += 1

        with open(output_m3u, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))

        print(f"✅ 生成 M3U 完成：共 {count} 个频道")
        print(f"✅ 文件保存为 {output_m3u}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        raise

if __name__ == "__main__":
    start_time = time.time()
    print("=" * 50)
    print("🎬 开始运行 channel_ai.py")
    print("=" * 50)
    main()
    print("=" * 50)
    print(f"🏁 程序结束，耗时: {round(time.time() - start_time, 2)}s")
    print("=" * 50)
