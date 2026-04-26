# -*- coding: utf-8 -*-
"""
最终版：
功能：下载根目录文件
"""
import os
import json

def parse_final(file_path):
    """最终解析逻辑"""
    result = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 按分类提取
            if "分类1" in line:
                result.append(line)
            elif "分类2" in line:
                result.append(line)
    return result

if __name__ == "__main__":
    # 直接解析根目录 data
    parse_final("data.txt")
