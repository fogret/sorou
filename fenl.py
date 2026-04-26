import os
import re
import time
import asyncio
import aiohttp
from collections import defaultdict

# ---------------- 配置 ----------------
INPUT_URL_FILE = "data.txt"      # 存放链接的文件
OUTPUT_FILE = "fenl_output.txt"  # 最终输出
CONCURRENCY = 20                 # 并发数（可根据网络调整）
TIMEOUT = 10                     # 下载超时秒数

# 分类关键词正则
CATEGORY_PATTERNS = {
    "央视频道": re.compile(r"央视|CCTV", re.IGNORECASE),
    "卫视频道": re.compile(r"卫视|中国.*卫视", re.IGNORECASE),
    "付费频道": re.compile(r"付费|HD|高清", re.IGNORECASE),
    "电影频道": re.compile(r"电影", re.IGNORECASE),
    "数字频道": re.compile(r"数字|TV|频道", re.IGNORECASE),
}

# 省份简称映射
PROVINCE_MAP = {
    "京": "北京", "津": "天津", "冀": "河北", "晋": "山西", "蒙": "内蒙古",
    "辽": "辽宁", "吉": "吉林", "黑": "黑龙江",
    "沪": "上海", "苏": "江苏", "浙": "浙江", "皖": "安徽", "闽": "福建", "赣": "江西", "鲁": "山东",
    "豫": "河南", "鄂": "湖北", "湘": "湖南", "粤": "广东", "桂": "广西", "琼": "海南",
    "渝": "重庆", "川": "四川", "贵": "贵州", "云": "云南",
    "陕": "陕西", "甘": "甘肃", "青": "青海", "宁": "宁夏", "新": "新疆",
}

# 存储结果
result = defaultdict(dict)          # 常规分类: {分类: {频道名: 链接}}
local_result = defaultdict(dict)   # 地方频道: {省份: {频道名: 链接}}

# ---------------- 下载工具 ----------------
async def fetch_url(session, url, semaphore, progress):
    async with semaphore:
        try:
            async with session.get(url, timeout=TIMEOUT) as resp:
                if resp.status in (200, 206):
                    text = await resp.text()
                    progress["success"] += 1
                    return text
                else:
                    progress["fail"] += 1
                    return None
        except Exception as e:
            progress["fail"] += 1
            return None

async def download_all(urls):
    semaphore = asyncio.Semaphore(CONCURRENCY)
    progress = {"success": 0, "fail": 0, "total": len(urls)}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url, semaphore, progress) for url in urls]
        results = await asyncio.gather(*tasks)

    print(f"下载完成：成功 {progress['success']} / 失败 {progress['fail']} / 总计 {progress['total']}")
    return [r for r in results if r is not None]

# ---------------- 解析频道 ----------------
def parse_channel_text(text):
    """解析 m3u / txt 内容，提取 #EXTINF 格式频道"""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # 匹配标准 EXTINF 格式
        m = re.match(r'#EXTINF:-?\d*\s*(.*?),(.+)', line)
        if m:
            attrs = m.group(1)
            name = m.group(2).strip()

            # 尝试从属性中提取 tvg-name
            name_match = re.search(r'tvg-name="([^"]+)"', attrs)
            if name_match:
                name = name_match.group(1).strip()

            # 下一行通常是链接
            if i + 1 < len(lines):
                link = lines[i + 1].strip()
                if link.startswith(("http://", "https://", "rtmp://", "udp://")):
                    classify_channel(name, link)

# ---------------- 分类逻辑 ----------------
def classify_channel(name, link):
    # 1. 常规分类匹配
    for cat, pat in CATEGORY_PATTERNS.items():
        if pat.search(name):
            if name not in result[cat]:
                result[cat][name] = link
            return

    # 2. 地方频道匹配
    # 匹配 省/市/自治区
    m = re.match(r'([^省市]+省|.+自治区|[^省市]+市)', name)
    if m:
        prov = m.group(1)
        # 标准化省份名
        for abbr, full in PROVINCE_MAP.items():
            if prov.startswith(full) or prov.startswith(abbr):
                prov = full
                break
        if name not in local_result[prov]:
            local_result[prov][name] = link
        return

# ---------------- 写入结果 ----------------
def write_result():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # 常规分类
        for cat in CATEGORY_PATTERNS:
            channels = result[cat]
            if channels:
                f.write(f"【{cat}】\n")
                for name in sorted(channels):
                    f.write(f"{name},{channels[name]}\n")
                f.write("\n")

        # 地方频道
        if local_result:
            f.write("【地方频道】\n")
            for prov in sorted(local_result):
                channels = local_result[prov]
                if channels:
                    f.write(f"  【{prov}】\n")
                    for name in sorted(channels):
                        f.write(f"    {name},{channels[name]}\n")
                    f.write("\n")

    print(f"结果已写入：{os.path.abspath(OUTPUT_FILE)}")

# ---------------- 主流程 ----------------
def main():
    if not os.path.exists(INPUT_URL_FILE):
        print(f"未找到文件：{INPUT_URL_FILE}")
        return

    with open(INPUT_URL_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().startswith(("http://", "https://", "rtmp://", "udp://"))]

    if not urls:
        print("data.txt 中未找到有效链接")
        return

    print(f"读取到 {len(urls)} 个链接，开始下载...")
    texts = asyncio.run(download_all(urls))

    for text in texts:
        parse_channel_text(text)

    write_result()

if __name__ == "__main__":
    main()
