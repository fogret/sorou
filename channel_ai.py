# channel_ai.py
import requests
import re

def main():
    print("📶 开始获取接口数据...")
    url = "https://cnb.cool/xiaomideyun/xiaomideyun/-/git/raw/main/mi.json"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        print(f"✅ 请求成功，状态码: {r.status_code}")
        content = r.text

        # 提取所有 http/https 链接
        links = re.findall(r'https?://[^\s"#]+', content)
        links = sorted(list(set(links)))  # 去重

        if not links:
            print("⚠️ 未提取到任何链接")
            return

        # 生成 M3U
        m3u = ["#EXTM3U"]
        for i, link in enumerate(links, 1):
            name = f"频道 {i}"
            m3u.append(f'#EXTINF:-1,{name}')
            m3u.append(link)

        with open("channels.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u))

        print(f"✅ 生成完成，共 {len(links)} 个频道")

    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    print("="*50)
    print("开始运行 channel_ai.py")
    print("="*50)
    main()
    print("="*50)
    print("运行结束")
    print("="*50)
