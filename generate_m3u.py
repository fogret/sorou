# -*- coding: utf-8 -*-
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

INPUT = "data.txt"
OUTPUT = "live.m3u"

logger.info("开始读取 data.txt")

try:
    with open(INPUT, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
except Exception as e:
    logger.error(f"读取失败: {e}")
    raise

seen_urls = set()
output = ['#EXTM3U']
current_name = None

url_pattern = re.compile(r'^https?://')

logger.info("开始解析频道...")

for line in lines:
    line = line.strip()
    if not line:
        continue

    # 匹配频道名称
    if line.startswith('#EXTINF'):
        current_name = line
        continue

    # 匹配 URL
    if url_pattern.match(line):
        url = line
        if url in seen_urls:
            logger.info(f"去重重复链接: {url}")
            continue

        seen_urls.add(url)
        if current_name:
            output.append(current_name)
            output.append(url)
        current_name = None

logger.info(f"原始记录: {len(lines)} 行")
logger.info(f"去重后有效频道: {len(seen_urls)} 个")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

logger.info(f"生成完成: {OUTPUT}")
