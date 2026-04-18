import requests
import json
import time
from datetime import datetime

# ================== 配置 ==================
SOURCE_URL = "https://raw.githubusercontent.com/fogret/sourt/master/config/subscribe.txt"
LOG_FILE = "channel_process.log"

# 强制分类，绝不出现未分类
CATEGORIES = [
    "央视", "卫视", "体育", "电影", "电视剧",
    "少儿", "新闻", "综艺", "音乐", "地方台", "港澳台", "海外"
]

# ================== 日志函数 ==================
def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now}] {message}"
    print(log_line)
    # 写入日志文件
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

# ================== AI 处理 ==================
def ai_standard_classify(raw_name):
    prompt = f"""
你是IPTV频道处理助手。
规则：
1. 清理名称，去掉 4K/HD/超清/测试/广告/乱码
2. 输出标准频道名
3. 从以下分类选 **唯一一个**，禁止未分类：
{CATEGORIES}
4. 只返回JSON，无其他内容

格式：
{{"name":"标准名称","category":"分类"}}

频道名：{raw_name}
"""

    # 国内可访问的免费AI接口（不会被墙）
    api_url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(api_url, json={
            "model": "moonshot-v1-8k",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }, timeout=20)

        result = resp.json()
        content = result["choices"][0]["message"]["content"].strip()
        data = json.loads(content)

        std_name = data.get("name", raw_name).strip()
        cate = data.get("category", "地方台")

        if cate not in CATEGORIES:
            cate = "地方台"

        return std_name, cate

    except Exception as e:
        log(f"AI接口异常，兜底分类：地方台 | 原因：{str(e)[:50]}")
        return raw_name.strip(), "地方台"

# ================== 下载并解析 ==================
def main():
    log("===== 任务开始 =====")
    log(f"开始下载订阅：{SOURCE_URL}")

    try:
        resp = requests.get(SOURCE_URL, timeout=30)
        resp.raise_for_status()
        log(f"下载成功，内容长度：{len(resp.text)} 字符")
    except Exception as e:
        log(f"下载失败：{str(e)}")
        return

    lines = resp.text.splitlines()
    channels = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "," in line:
            name_part, _, url = line.rpartition(",")
            url = url.strip()
            if url.startswith("http"):
                channels.append((name_part.strip(), url))

    log(f"解析完成，共获取频道：{len(channels)} 个")

    # 分组
    groups = {cat: [] for cat in CATEGORIES}
    used_url = set()

    for idx, (name_part, url) in enumerate(channels, 1):
        if url in used_url:
            log(f"[{idx}/{len(channels)}] 跳过重复：{url[:40]}...")
            continue
        used_url.add(url)

        log(f"[{idx}/{len(channels)}] AI处理：{name_part[:30]}...")
        std_name, cate = ai_standard_classify(name_part)
        groups[cate].append((std_name, url))
        time.sleep(1)

    # 输出 TXT
    log("开始写入 channels_output.txt")
    with open("channels_output.txt", "w", encoding="utf-8") as f:
        for cate in CATEGORIES:
            lst = groups[cate]
            if not lst:
                continue
            f.write(f"# {cate}\n")
            for n, u in lst:
                f.write(f"{n},{u}\n")
            f.write("\n")

    # 输出 M3U
    log("开始写入 channels_output.m3u")
    with open("channels_output.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cate in CATEGORIES:
            for n, u in groups[cate]:
                f.write(f"#EXTINF:-1,[{cate}]{n}\n{u}\n")

    log("全部完成！无未分类频道")
    log("===== 任务结束 =====\n")

if __name__ == "__main__":
    main()
