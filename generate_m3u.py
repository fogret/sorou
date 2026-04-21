# -*- coding: utf-8 -*-
import re
import logging

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

INPUT_PATH = "data.txt"
OUTPUT_PATH = "output.m3u"

logger.info("开始读取 data.txt")

try:
    with open(INPUT_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    logger.info("读取文件成功")
except FileNotFoundError:
    logger.error("错误：未找到 data.txt 文件")
    raise

# 匹配频道名 + URL
pattern = re.compile(r'^(.*?)(https?://.+)', re.MULTILINE)
seen_urls = set()
m3u_lines = ['#EXTM3U']

matches = pattern.findall(content)
logger.info(f"匹配到 {len(matches)} 条链接记录")

for name_part, url in matches:
    url = url.strip()
    if not url:
        continue

    if url in seen_urls:
        logger.info(f"去重跳过重复URL: {url}")
        continue

    seen_urls.add(url)
    name = name_part.strip() or "未知频道"

    m3u_lines.append(f'#EXTINF:-1,{name}')
    m3u_lines.append(url)

logger.info(f"去重后有效频道总数: {len(seen_urls)}")

# 写入 m3u
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(m3u_lines))

logger.info(f"生成完成: {OUTPUT_PATH}")
