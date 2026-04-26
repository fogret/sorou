# -*- coding: utf-8 -*-
import os
from datetime import datetime

LOG_FILE = "run_log.txt"

def log(message):
    """写入日志 + 同时打印"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now}] {message}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def main():
    log("=== 开始执行 fenl.py ===")

    data_file = "data.txt"
    output_file = "fenl_output.txt"

    # 1. 检查文件
    log("步骤 1：检查 data.txt 是否存在")
    if not os.path.exists(data_file):
        log(f"错误：{data_file} 不存在")
        return
    log(f"找到：{data_file}")

    # 2. 读取文件
    log("步骤 2：开始读取 data.txt")
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        log(f"读取完成，共 {len(lines)} 行")
    except Exception as e:
        log(f"读取失败：{e}")
        return

    # 3. 解析分类与频道
    log("步骤 3：开始解析分类和频道名")
    result = {}
    channel_set = set()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        if len(parts) >= 2:
            category = parts[0].strip()
            channel = parts[1].strip()

            if category and channel:
                if category not in result:
                    result[category] = set()
                result[category].add(channel)
                channel_set.add(channel)

    log(f"解析完成：共识别到 {len(channel_set)} 个不重复频道")

    # 4. 写入输出
    log("步骤 4：写入 fenl_output.txt")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for cat, chans in result.items():
                f.write(f"{cat}:\n")
                for ch in sorted(chans):
                    f.write(f"  - {ch}\n")
                f.write("\n")
        log(f"写入完成：{output_file}")
    except Exception as e:
        log(f"写入失败：{e}")
        return

    log("=== 执行完成 ===")

if __name__ == "__main__":
    main()
