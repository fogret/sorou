# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict

# 配置文件路径
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 1. 定义你的原始分类规则（保持不变）
CATEGORY_PATTERNS = {
    "央视频道": re.compile(r"央视|CCTV", re.IGNORECASE),
    "卫视频道": re.compile(r"卫视|中国.*卫视", re.IGNORECASE),
    "付费频道": re.compile(r"付费|HD|高清", re.IGNORECASE),
    "电影频道": re.compile(r"电影", re.IGNORECASE),
    "数字频道": re.compile(r"数字|TV|频道", re.IGNORECASE),
}

# 2. 省份简称与全称映射表（用于精准归类）
PROVINCE_MAP = {
    "京": "北京", "津": "天津", "冀": "河北", "晋": "山西", "蒙": "内蒙古",
    "辽": "辽宁", "吉": "吉林", "黑": "黑龙江",
    "沪": "上海", "苏": "江苏", "浙": "浙江", "皖": "安徽", "闽": "福建", "赣": "江西", "鲁": "山东",
    "豫": "河南", "鄂": "湖北", "湘": "湖南", "粤": "广东", "桂": "广西", "琼": "海南",
    "渝": "重庆", "川": "四川", "贵": "贵州", "云": "云南",
    "陕": "陕西", "甘": "甘肃", "青": "青海", "宁": "宁夏", "新": "新疆",
    # 可根据需要补充
}

# 存储结构
channel_classified = defaultdict(set)  # 大分类: {频道名: 链接}
channel_provinces = defaultdict(dict)  # 省份: {频道名: 链接}

def parse_and_classify():
    """解析 data.txt 并完成分类和省份归并"""
    if not os.path.exists(INPUT_FILE):
        print(f"错误：未找到文件 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    channel_name = ""
    channel_link = ""

    for i, line in enumerate(lines):
        # 匹配 #EXTINF 行获取频道名
        if line.startswith("#EXTINF"):
            # 提取 , 后面的名称
            name_match = re.search(r',(.+)', line)
            if name_match:
                channel_name = name_match.group(1).strip()
                # 获取下一行的链接
                if i + 1 < len(lines):
                    channel_link = lines[i+1]
                    continue
        # 如果当前行是链接且上一行解析到了名称
        elif channel_name and line.startswith(("http://", "https://", "rtmp://", "udp://")):
            channel_link = line

        # 当名称和链接都存在时，开始处理分类
        if channel_name and channel_link:
            process_channel(channel_name, channel_link)
            # 重置，等待下一个频道
            channel_name = ""
            channel_link = ""

def process_channel(name, link):
    """处理单个频道：进行大分类和省份归并"""
    # --- 步骤 1：进行原始大分类 ---
    main_category = "地方频道" # 默认归为地方
    for cat, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(name):
            main_category = cat
            break

    # 去重存储（使用set自动去重）
    channel_classified[main_category].add((name, link))

    # --- 步骤 2：进行省份归并 ---
    province_name = "未知省份"
    # 优先匹配全称 (如 河南省电视台)
    for abbr, full in PROVINCE_MAP.items():
        if full in name or abbr in name:
            province_name = full
            break
    
    # 如果没匹配到，尝试匹配简称（如 河南台）
    if province_name == "未知省份":
        for abbr, full in PROVINCE_MAP.items():
            if abbr in name:
                province_name = full
                break

    # 存入省份分类
    channel_provinces[province_name][name] = link

def write_output():
    """写入最终文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=== 按原始分类 ===\n\n")
        
        # 写入原始分类
        for cat in ["央视频道", "卫视频道", "付费频道", "电影频道", "数字频道", "地方频道"]:
            channels = channel_classified.get(cat, set())
            if channels:
                f.write(f"【{cat}】\n")
                for name, link in sorted(channels):
                    f.write(f"{name},{link}\n")
                f.write("\n")

        f.write("="*50 + "\n")
        f.write("=== 按省份详细分类 ===\n\n")
        
        # 写入按省份分类
        for prov in sorted(channel_provinces.keys()):
            channels = channel_provinces[prov]
            if channels:
                f.write(f"【{prov}】\n")
                for name, link in sorted(channels.items()):
                    f.write(f"  {name},{link}\n")
                f.write("\n")

    print(f"处理完成！结果已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_and_classify()
    write_output()
