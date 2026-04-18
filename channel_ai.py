# channel_ai.py
import requests
import json
from urllib.parse import urljoin

def fetch_and_convert_to_m3u():
    json_url = "https://cnb.cool/xiaomideyun/xiaomideyun/-/git/raw/main/mi.json"
    output_m3u = "channels.m3u"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.get(json_url, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        m3u_lines = ["#EXTM3U"]
        count = 0

        for cat in data.get("data", {}).get("list", []):
            category = cat.get("type_name", "未分类").strip()
            channels = cat.get("vod_list", [])

            for ch in channels:
                name = ch.get("title", "未知频道").strip()
                play_url = ch.get("play_url", "").strip()
                if not play_url:
                    continue

                play_url = urljoin(json_url, play_url)
                m3u_lines.append(f'#EXTINF:-1 tvg-name="{name}" group-title="{category}",{name}')
                m3u_lines.append(play_url)
                count += 1

        with open(output_m3u, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))

        print(f"✅ 转换完成！已生成：{output_m3u}")
        print(f"📺 共提取频道：{count} 个")

    except Exception as e:
        print(f"❌ 出错：{e}")

if __name__ == "__main__":
    fetch_and_convert_to_m3u()
