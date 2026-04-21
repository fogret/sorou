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
    with open(INPUT, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
except Exception as e:
    logger.error(f"读取文件失败: {e}")
    raise

pattern = re.compile(r"^(.*?)(https?://\S+)", re.MULTILINE)
matches = pattern.findall(content)
logger.info(f"匹配到 {len(matches)} 条记录")

seen = set()
m3u = ["#EXTM3U"]

for name_part, url in matches:
    url = url.strip()
    if url in seen:
        logger.info(f"去重: {url}")
        continue
    seen.add(url)
    name = name_part.strip() or "未知频道"
    m3u.append(f"#EXTINF:-1,{name}")
    m3u.append(url)

logger.info(f"最终频道数量: {len(seen)}")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(m3u))

logger.info(f"生成完成: {OUTPUT}")
