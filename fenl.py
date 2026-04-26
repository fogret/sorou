# 最终版：GitHub Actions 兼容
# fenlei.py
import os
import json

def parse_github_data(data_file="data.txt"):
    """
    解析 GitHub 相关的分类和频道
    格式：分类名|频道名|链接
    """
    result = {}
    if not os.path.exists(data_file):
        print(f"错误：未找到 {data_file}")
        return result

    # 示例格式：分类A|频道1|链接1
    # 解析分类、频道、链接
    for line in open(data_file, "r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        if len(parts) >= 3:
            category = parts[0].strip()
            channel = parts[1].strip()
            link = parts[2].strip()

            if category not in result:
                result[category] = []
            result[category].append({
                "频道": channel,
                "链接": link
            })

    return result

def main():
    data = parse_github_data("data.txt")
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
