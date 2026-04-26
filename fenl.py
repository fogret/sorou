# 1. 导入必要的库：用于文件操作、正则表达式匹配
import os
import re

# 2. 定义输入输出文件路径
INPUT_FILE = "data.txt"
OUTPUT_FILE = "fenl_output.txt"

# 3. 定义分类关键词和对应的正则匹配模式
#    键：分类名称，值：用于匹配频道分类的正则表达式
CATEGORY_PATTERNS = {
    "央视频道": re.compile(r"央视|CCTV"),
    "卫视频道": re.compile(r"卫视|中国.*卫视"),
    "付费频道": re.compile(r"付费|HD|高清"),
    "电影频道": re.compile(r"电影"),
    "数字频道": re.compile(r"数字|TV"),
    # 地方频道需特殊处理，后续单独按省份匹配
}

# 4. 定义中国大陆省份简称与全称的映射，用于解析地方频道
PROVINCE_MAP = {
    "京": "北京", "津": "天津", "冀": "河北", "晋": "山西", "蒙": "内蒙古",
    "辽": "辽宁", "吉": "吉林", "黑": "黑龙江",
    "沪": "上海", "苏": "江苏", "浙": "浙江", "皖": "安徽", "闽": "福建", "赣": "江西", "鲁": "山东",
    "豫": "河南", "鄂": "湖北", "湘": "湖南", "粤": "广东", "桂": "广西", "琼": "海南",
    "渝": "重庆", "川": "四川", "贵": "贵州", "云": "云南",
    "陕": "陕西", "甘": "甘肃", "青": "青海", "宁": "宁夏", "新": "新疆",
    # 可根据需要补充其他省份
}

# 5. 初始化数据结构，用于存储去重后的频道信息
#    结构：{分类名: {频道名: 链接}}
channel_data = {}
for category in CATEGORY_PATTERNS.keys():
    channel_data[category] = {}

# 地方频道单独存储，结构：{省份名: {频道名: 链接}}
local_channels = {}

# 6. 读取并解析根目录下的data.txt文件
def parse_data_file(file_path):
    """
    解析data.txt文件，提取频道链接和名称
    """
    if not os.path.exists(file_path):
        print(f"错误：未找到文件 {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 7. 尝试匹配链接和频道名的模式
        #    常见格式：#EXTINF:-1 tvg-name="频道名" tvg-id="",链接地址
        match = re.match(r'#EXTINF:-1\s+tvg-name="([^"]+)"\s+tvg-id="[^"]*",\s*(.+)', line)
        if match:
            channel_name = match.group(1).strip()
            link = match.group(2).strip()
            classify_channel(channel_name, link)

# 8. 定义频道分类逻辑
def classify_channel(channel_name, link):
    """
    根据频道名将频道分类并去重存储
    """
    # 优先按预设分类匹配
    for category, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(channel_name):
            # 去重：如果该频道名不存在于该分类中，则添加
            if channel_name not in channel_data[category]:
                channel_data[category][channel_name] = link
            return

    # 未匹配到预设分类，尝试匹配地方频道
    match_province = re.match(r'([^省市]+省|.+自治区|[^省市]+市)', channel_name)
    if match_province:
        province = match_province.group(1)
        # 简化省份名（如“北京市”->“北京”）
        for abbr, full in PROVINCE_MAP.items():
            if province.startswith(full) or province.startswith(abbr):
                province = full
                break
        # 初始化省份存储
        if province not in local_channels:
            local_channels[province] = {}
        # 去重并添加
        if channel_name not in local_channels[province]:
            local_channels[province][channel_name] = link
        return

    # 9. 未匹配到任何分类的频道，可根据需要处理
    #    这里暂时忽略，也可添加到“其他分类”

# 10. 执行解析
parse_data_file(INPUT_FILE)

# 11. 将解析结果写入输出文件fenl_output.txt
def write_output_file():
    """
    将分类后的频道信息写入输出文件
    """
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 写入预设分类
        for category, channels in channel_data.items():
            if channels:
                f.write(f"【{category}】\n")
                for name, link in sorted(channels.items()):
                    f.write(f"{name},{link}\n")
                f.write("\n")

        # 写入地方频道分类
        if local_channels:
            f.write("【地方频道】\n")
            for province, channels in sorted(local_channels.items()):
                f.write(f"  【{province}】\n")
                for name, link in sorted(channels.items()):
                    f.write(f"    {name},{link}\n")
                f.write("\n")

    print(f"解析完成！结果已保存至 {OUTPUT_FILE}")

# 12. 执行写入
write_output_file()
