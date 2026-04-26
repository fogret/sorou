# -*- coding: utf-8 -*-
import os

def main():
    input_file = "data.txt"
    output_file = "fenl_output.txt"

    if not os.path.exists(input_file):
        print("错误：未找到 data.txt")
        return

    # 直接读取你真实的频道数据（不需要 requests）
    lines = []
    with open(input_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("错误：data.txt 为空")
        return

    # 原始格式示例：
    # #EXTINF:-1 group-title="河南电信-组播1",河南卫视
    groups = {}

    for line in lines:
        if "group-title=" in line:
            # 提取分组名
            g = line.split('group-title="')[1].split('"')[0]
            # 提取频道名
            chan = line.split(",")[-1].strip()

            if g not in groups:
                groups[g] = []
            groups[g].append(chan)

    # 去重
    for g in groups:
        groups[g] = list(set(groups[g]))

    # 写入
    with open(output_file, "w", encoding="utf-8") as f:
        for g, chans in groups.items():
            f.write(f"【{g}】\n")
            for c in chans:
                f.write(f" - {c}\n")
            f.write("\n")

    print(f"完成！结果已写入：{output_file}")

if __name__ == "__main__":
    main()
