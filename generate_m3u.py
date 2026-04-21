# -*- coding: utf-8 -*-
import re
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

INPUT = "data.txt"
OUTPUT = "live.m3u"
TIMEOUT = 10

# 读取播放源链接
with open(INPUT, "r", encoding="utf-8", errors="ignore") as f:
    source_urls = [line.strip() for line in f if line.strip()]

logger.info(f"开始读取 {len(source_urls)} 个订阅源")

seen_urls = set()
m3u = ["#EXTM3U"]
current_name = None

url_pattern = re.compile(r"^https?://")

# 遍历下载每个源
for idx, url in enumerate(source_urls, 1):
    logger.info(f"[{idx}/{len(source_urls)}] 下载: {url}")
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        lines = resp.text.splitlines()
    except Exception as e:
        logger.warning(f"下载失败: {e}")
        continue

    # 解析频道
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF"):
            current_name = line
            continue

        if url_pattern.match(line):
            u = line
            if u in seen_urls:
                continue
            seen_urls.add(u)
            if current_name:
                m3u.append(current_name)
                m3u.append(u)
            current_name = None

logger.info(f"原始总链接数: {len(source_urls)}")
logger.info(f"去重后总频道: {len(seen_urls)} 个")

# 写入
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))

logger.info(f"生成完成: {OUTPUT}")
