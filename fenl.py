# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime

def log(message, log_file="run_log.txt"):
    """写日志，带时间戳"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)

def main():
    input_file = "data.txt"
    output_file = "fenl_output.txt"
    log_file = "run_log.txt"

    log("=== 开始运行 fenl.py ===")

    # 检查文件
    if not os.path.exists(input_file):
        error = f"错误：未找到文件 {input_file}"
        log(error)
        print(error)
        return

    # 读取 URL
    urls = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(("http://", "https://")):
                urls.append(line)

    if not urls:
        error = "错误：data.txt 中无有效链接"
        log(error)
        print(error)
        return

    log(f"读取到 {len(urls)} 个链接")

    # 解析分组与频道
    groups = {}
    for url in urls:
        log(f"正在处理: {url}")
        try:
            # 你真实解析逻辑在此
            # 以下为示例，请替换成你真实的解析代码
            # 示例：
            # content = requests.get(url, timeout=10).text
            # 然后按 #EXTINF group-title 解析

            # 模拟解析（请替换成真实解析代码）
            mock_group = "测试分组"
            mock_chan = "测试频道"

            if mock_group not in groups:
                groups[mock_group] = []
            groups[mock_group].append(mock_chan)

        except Exception as e:
            log(f"解析失败 {url} → {str(e)}")
            continue

    # 去重
    for g in groups:
        unique = list(set(groups[g]))
        groups[g] = unique

    # 写入最终结果
    with open(output_file, "w", encoding="utf-8") as f:
        for g in groups:
            f.write(f"{g}\n")
            for chan in groups[g]:
                f.write(f"- {chan}\n")

    log(f"完成！结果写入 {output_file}")
    print("完成！结果已写入：" + output_file)

if __name__ == "__main__":
    main()
