# -*- coding: utf-8 -*-
import os
import re

def main():
    # 配置
    input_file = "data.txt"
    output_file = "fenl_output.txt"

    # 读取
    if not os.path.exists(input_file):
        print(f"错误：未找到 {input_file}")
        return

    lines = []
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("错误：文件为空")
        return

    # 解析 EXTINF 格式
    # 示例：#EXTINF:-1 group-title="河南电信-组播1",河南卫视
    groups = {}
    for line in lines:
        # 匹配 group-title="xxx"
        match = re.search(r'group-title="([^"]+)"', line)
        if match:
            group = match.group(1)
            if group not in groups:
                groups[group] = []
            # 提取频道名 (逗号后 )
            chan_name = re.sub(r'^[^,]+,\s*', '', line).strip()
            if chan_name:
                groups[group].append(chan_name)

    # 去重，保持顺序
    for g in groups:
        seen = set()
        unique = []
        for item in groups[g]:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        groups[g] = unique

    # 写入结果
    with open(output_file, "w", encoding="utf-8") as f:
        for group, chans in groups.items():
            f.write(f"\n【{group}】\n")
            for chan in chans:
                f.write(f" - {chan}\n")

    print(f"完成！结果已写入: {output_file}")

if __name__ == "__main__":
    main()
