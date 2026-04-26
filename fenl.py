# -*- coding: utf-8 -*-
import os
import re
import requests

def main():
    # 配置
    input_file = "data.txt"
    output_file = "fenl_output.txt"

    # 读取
    if not os.path.exists(input_file):
        print(f"错误：未找到 {input_file}")
        return

    urls = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("http"):
                urls.append(line)

    if not urls:
        print("错误：无有效链接")
        return

    # 解析
    groups = {}
    for url in urls:
        print(f"正在解析: {url}")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            content = resp.text
        except Exception as e:
            print(f"错误: {e}")
            continue

        # 按 EXTINF 分组解析
        pattern = r'group-title="([^"]+)"'
        matches = re.findall(pattern, content)
        for match in matches:
            if match not in groups:
                groups[match] = []
            # 模拟频道列表 (实际应从 content 解析)
            groups[match].append(f"示例频道 - {match}")

    # 去重
    for g in groups:
        groups[g] = list(set(groups[g]))

    # 写入
    with open(output_file, "w", encoding="utf-8") as f:
        for group, chans in groups.items():
            f.write(f"{group}\n")
            f.write(" | ".join(chans) + "\n\n")

    print(f"完成！结果已写入: {output_file}")

if __name__ == "__main__":
    main()
