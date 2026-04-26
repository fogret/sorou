# -*- coding: utf-8 -*-
"""
最终版：解析 data.txt，提取分类名和频道名
输出格式：分类名: 频道名1, 频道名2, ...
无链接、无多余、无废话
"""

import os
from collections import OrderedDict

def parse_and_deduplicate(data_file="data.txt", output_file="fenl_output.txt"):
    """
    解析 data.txt，提取：
    1. 分类名（第一列）
    2. 频道名（第二列）
    输出：fenl_output.txt（无链接、无多余）
    """

    # 存储结果：分类 -> [频道1, 频道2, ...]
    result = OrderedDict()

    if not os.path.exists(data_file):
        print(f"错误：未找到数据文件 {data_file}")
        return result

    with open(data_file, "r", encoding="utf-8") as f:
        for line_num, line_content in enumerate(f, 1):
            line = line_content.strip()
            if not line:
                continue

            # 解析格式：分类名|频道名|链接（忽略链接，只取前两个）
            parts = line.split("|")
            if len(parts) < 2:
                continue

            category = parts[0].strip()      # 分类名（第一列）
            channel_name = parts[1].strip()  # 频道名（第二列）

            if not category or not channel_name:
                continue

            # 去重
            if category not in result:
                result[category] = []
            if channel_name not in result[category]:
                result[category].append(channel_name)

    # 写入输出文件
    with open(output_file, "w", encoding="utf-8") as fo:
        for cat, channels in result.items():
            fo.write(f"{cat}:\n")
            for ch in channels:
                fo.write(f"  - {ch}\n")
            fo.write("\n")

    print(f"完成！结果已写入 {output_file}")
    return result

if __name__ == "__main__":
    parse_and_deduplicate()
