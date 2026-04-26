# -*- coding: utf-8 -*-
import os

def main():
    """
    最终版日志处理脚本
    读取 data.txt → 解析链接 → 输出到 fenl_output.txt
    """
    input_file = "data.txt"
    output_file = "fenl_output.txt"

    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：未找到 {input_file}")
        return

    # 读取并解析
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 模拟解析（你可替换成真实解析逻辑）
    lines = content.splitlines()
    result = []

    for line in lines:
        if "group=" in line or "title=" in line:
            result.append(line.strip())

    # 写入结果
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(result))

    print(f"完成！结果已保存到 {output_file}")

if __name__ == "__main__":
    main()
