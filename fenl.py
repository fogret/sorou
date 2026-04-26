import os
import re
import time
import asyncio
import aiohttp
from collections import defaultdict
import sys

# ---------------- 配置 ----------------
INPUT_URL_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"
CONCURRENCY = 20
TIMEOUT = 15

# 调试模式：从环境变量读取，Actions 中设为 true
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

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
result = defaultdict(dict)
local_result = defaultdict(dict)

# ---------------- 调试日志工具 ----------------
def log(message, level="INFO"):
    """统一打印日志，带时间戳"""
    from datetime import datetime
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {message}")

# ---------------- 下载工具 ----------------
async def fetch_url(session, url, semaphore, progress):
    async with semaphore:
        try:
            log(f"开始下载: {url[:50]}...", "DEBUG")
            async with session.get(url, timeout=TIMEOUT) as resp:
                if resp.status in (200, 206):
                    text = await resp.text()
                    progress["success"] += 1
                    # 调试：打印下载内容的前500个字符
                    if DEBUG:
                        log(f"下载成功，内容前500字符: {text[:500]}", "DEBUG")
                    return text
                else:
                    progress["fail"] += 1
                    log(f"下载失败，状态码: {resp.status}", "ERROR")
                    return None
        except Exception as e:
            progress["fail"] += 1
            log(f"下载异常: {str(e)}", "ERROR")
            return None

async def download_all(urls):
    semaphore = asyncio.Semaphore(CONCURRENCY)
    progress = {"success": 0, "fail": 0, "total": len(urls)}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url, semaphore, progress) for url in urls]
        results = await asyncio.gather(*tasks)

    log(f"下载完成：成功 {progress['success']} / 失败 {progress['fail']} / 总计 {progress['total']}")
    # 调试：打印有效下载数量
    valid_texts = [r for r in results if r is not None]
    log(f"有效下载内容数量: {len(valid_texts)}")
    return valid_texts

# ---------------- 解析频道 ----------------
def parse_channel_text(text):
    """解析 m3u / txt 内容，提取 #EXTINF 格式频道"""
    if not text:
        log("跳过空内容解析", "WARNING")
        return

    lines = text.splitlines()
    log(f"开始解析文本，共 {len(lines)} 行", "DEBUG")

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
                    # 调试：打印每一个匹配到的频道
                    if DEBUG:
                        log(f"匹配到频道 -> 名称: {name}, 链接: {link[:50]}...", "DEBUG")
                    classify_channel(name, link)
        # 调试：如果一行都没匹配到，打印出来看看是什么格式
        elif DEBUG and i < 20:  # 只打印前20行，避免刷屏
            log(f"未匹配到 EXTINF 格式行: {line}", "DEBUG")

# ---------------- 分类逻辑 ----------------
def classify_channel(name, link):
    # 1. 常规分类匹配
    for cat, pat in CATEGORY_PATTERNS.items():
        if pat.search(name):
            if name not in result[cat]:
                result[cat][name] = link
            return

    # 2. 地方频道匹配
    m = re.match(r'([^省市]+省|.+自治区|[^省市]+市)', name)
    if m:
        prov = m.group(1)
        for abbr, full in PROVINCE_MAP.items():
            if prov.startswith(full) or prov.startswith(abbr):
                prov = full
                break
        if name not in local_result[prov]:
            local_result[prov][name] = link
        return

# ---------------- 写入结果 ----------------
def write_result():
    """写入结果并打印统计信息"""
    # 调试：打印最终统计
    total_channels = sum(len(channels) for channels in result.values()) + sum(len(channels) for channels in local_result.values())
    log(f"最终解析到的频道总数: {total_channels}")

    if total_channels == 0:
        log("警告：没有解析到任何频道，可能是链接格式不对或内容为空", "WARNING")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # 常规分类
        for cat in CATEGORY_PATTERNS:
            channels = result[cat]
            if channels:
                f.write(f"【{cat}】\n")
                log(f"  {cat}: {len(channels)} 个", "INFO")
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
                    log(f"    {prov}: {len(channels)} 个", "INFO")
                    for name in sorted(channels):
                        f.write(f"    {name},{channels[name]}\n")
                    f.write("\n")

    log(f"结果已写入: {os.path.abspath(OUTPUT_FILE)}")

# ---------------- 主流程 ----------------
def main():
    log("=== 开始执行 fenl.py 调试模式 ===")

    if not os.path.exists(INPUT_URL_FILE):
        log(f"错误：未找到文件 {INPUT_URL_FILE}", "FATAL")
        return

    # 调试：打印 data.txt 内容
    with open(INPUT_URL_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        log(f"data.txt 内容: {content}")
        urls = [line.strip() for line in content.splitlines() if line.strip().startswith(("http://", "https://", "rtmp://", "udp://"))]

    if not urls:
        log("错误：data.txt 中未找到有效链接", "FATAL")
        return

    log(f"读取到 {len(urls)} 个有效链接")
    texts = asyncio.run(download_all(urls))

    for text in texts:
        parse_channel_text(text)

    write_result()

if __name__ == "__main__":
    main()
