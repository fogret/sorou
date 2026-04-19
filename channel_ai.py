# channel_ai.py
import urllib.request
import re

def scan_m3u():
    # 目标m3u地址
    url = "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u"
    
    # 请求头，解决访问限制
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print("正在下载并解析频道列表...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as f:
            content = f.read().decode('utf-8', errors='ignore')

        # 存储结果
        result = []
        current_group = "未分类"

        # 逐行解析
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 提取分类 group-title
            if 'group-title="' in line:
                g = re.search(r'group-title="([^"]+)"', line)
                if g:
                    current_group = g.group(1).strip()

            # 提取频道名 tvg-name
            if line.startswith("#EXTINF:"):
                n = re.search(r'tvg-name="([^"]+)"', line)
                if n:
                    channel_name = n.group(1).strip()
                    result.append(f"[{current_group}] {channel_name}")

        # 去重 + 排序
        result = sorted(list(set(result)))

        # 写入根目录 txt
        save_path = "频道分类列表.txt"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"扫描完成，共 {len(result)} 个频道\n")
            f.write("="*40 + "\n")
            f.write("\n".join(result))

        print(f"✅ 完成！文件已保存到：{save_path}")
        print(f"📺 频道总数：{len(result)}")

    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        print("💡 建议：检查网络，或挂代理后重新运行")

if __name__ == "__main__":
    scan_m3u()
