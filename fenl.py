# -*- coding: utf-8 -*-
import os
import re
import requests
from collections import defaultdict

# 配置文件路径
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 1. 原始大分类规则 (保持不变)
CATEGORY_PATTERNS = {
    "央视频道": re.compile(r"央视|CCTV", re.IGNORECASE),
    "卫视频道": re.compile(r"卫视|中国.*卫视", re.IGNORECASE),
    "付费频道": re.compile(r"付费|HD|高清", re.IGNORECASE),
    "电影频道": re.compile(r"电影", re.IGNORECASE),
    "数字频道": re.compile(r"数字|TV|频道", re.IGNORECASE),
}

# 2. 省份简称与全称映射表 (用于精准归类)
PROVINCE_MAP = {
    "京": "北京", "津": "天津", "冀": "河北", "晋": "山西", "蒙": "内蒙古",
    "辽": "辽宁", "吉": "吉林", "黑": "黑龙江",
    "沪": "上海", "苏": "江苏", "浙": "浙江", "皖": "安徽", "闽": "福建", "赣": "江西", "鲁": "山东",
    "豫": "河南", "鄂": "湖北", "湘": "湖南", "粤": "广东", "桂": "广西", "琼": "海南",
    "渝": "重庆", "川": "四川", "贵": "贵州", "云": "云南",
    "陕": "陕西", "甘": "甘肃", "青": "青海", "宁": "宁夏", "新": "新疆",
    # 可根据需要补充
}

# 3. 存储结构
#    key: 分类名 (如 央视频道、卫视频道)
#    value: set {频道名}
classified_channels = defaultdict(set)

#    key: 省份名 (如 河南省、江苏省)
#    value: set {频道名}
province_channels = defaultdict(set)

def download_and_parse_m3u(url):
    """下载远程 M3U 文件并提取频道名"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"下载失败: {e}")
        return []

    channels = []
    current_name = None

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            # 提取 #EXTINF 后面 , 之前的名称
            name_match = re.search(r',(.+)', line)
            if name_match:
                current_name = name_match.group(1).strip()
        elif current_name and line.startswith(("http://", "https://", "rtmp://", "udp://", "rtp://")):
            # 遇到链接且有名称，说明是一个完整频道
            channels.append(current_name)
            current_name = None # 重置，准备下一个

    return channels

def classify_and_append(name):
    """
    处理单个频道名：
    1. 判断属于哪个大分类
    2. 判断属于哪个省份
    3. 存入对应集合 (自动去重)
    """
    # --- 步骤 1: 归类到原始大分类 ---
    main_category = "地方频道" # 默认归为地方
    for cat, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(name):
            main_category = cat
            break
    # 添加到分类集合 (自动去重)
    classified_channels[main_category].add(name)

    # --- 步骤 2: 归类到具体省份 ---
    target_province = "未知省份"
    # 优先匹配全称 (如 河南省电视台)
    for abbr, full in PROVINCE_MAP.items():
        if full in name or abbr in name:
            target_province = full
            break
    # 添加到省份集合 (自动去重)
    province_channels[target_province].add(name)

def write_result():
    """写入最终结果到文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 写入 原始分类 (不含地方频道的拆分，只保留大类)
        f.write("=== 按原始分类 ===\n\n")
        # 按指定顺序写入
        order = ["央视频道", "卫视频道", "付费频道", "电影频道", "数字频道", "地方频道"]
        for cat in order:
            names = classified_channels.get(cat, set())
            if names:
                f.write(f"【{cat}】\n")
                for name in sorted(names):
                    f.write(f"{name}\n")
                f.write("\n")

        # 写入 按省份详细分类 (核心需求)
        f.write("="*50 + "\n")
        f.write("=== 按省份详细分类 ===\n\n")
        for province in sorted(province_channels.keys()):
            names = province_channels[province]
            if names: # 只写入有内容的省份
                f.write(f"【{province}】\n")
                for name in sorted(names):
                    f.write(f"  {name}\n") # 缩进一点，更清晰
                f.write("\n")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print("错误：未找到 data.txt")
        exit(1)

    # 读取 data.txt 中的远程链接
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip().startswith("http")]

    if not urls:
        print("错误：data.txt 中未找到有效链接")
        exit(1)

    # 全局去重：遍历所有链接，提取所有频道名
    all_channel_names = set()
    for url in urls:
        print(f"正在处理: {url}")
        channel_names = download_and_parse_m3u(url)
        all_channel_names.update(channel_names) # 自动去重

    print(f"共解析到 {len(all_channel_names)} 个不重复频道")

    # 分类处理
    for name in all_channel_names:
        classify_and_append(name)

    # 写入文件
    write_result()
    print(f"✅ 完成！结果已保存到 {OUTPUT_FILE}")
