# -*- coding: utf-8 -*-
import os

def main():
    input_path = "data.txt"
    output_path = "fenl_output.txt"

    if not os.path.exists(input_path):
        print("未找到 data.txt")
        return

    # 读取数据
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析：按行解析分组名与频道名
    lines = content.splitlines()
    groups = {}
    current_group = None

    for line in lines:
        if "group=" in line:
            # 提取分组名
            parts = line.split('group="')
            if len(parts) > 1:
                current_group = parts[1].split('"')[0]
                continue

        if "title=" in line:
            # 提取频道名
            parts = line.split('title="')
            if len(parts) > 1:
                name = parts[1].split('"')[0]
                if current_group:
                    if current_group not in groups:
                        groups[current_group] = []
                    groups[current_group].append(name)

    # 去重
    for g in groups:
        unique = []
        for x in groups[g]:
            if x not in unique:
                unique.append(x)
        groups[g] = unique

    # 输出
    with open(output_path, "w", encoding="utf-8") as f:
        for g in groups:
            f.write(f"{g}\n")
            for name in groups[g]:
                f.write(f"- {name}\n")

    print(f"完成，结果已输出到: {output_path}")

if __name__ == "__main__":
    main()
