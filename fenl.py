import re
import os
import time
import requests
from collections import defaultdict

# ===================== 基础配置 =====================
INPUT_FILE  = "data.txt"       # 源链接文件
OUTPUT_FILE = "fenl_output.txt"# 输出文件
TIMEOUT     = 15

# ===================== 分类关键词 =====================
CCTV_KEYS    = ["CCTV", "央视", "中央", "CETV", "CGTN", "新闻", "综合", "财经", "综艺", "体育", "电影", "军事", "科教", "戏曲", "社会与法", "少儿", "音乐", "体育赛事"]
SAT_KEYS     = ["卫视", "旅游", "教育", "少儿", "卡通", "动画", "综艺", "纪实", "科教"]
MOVIE_KEYS   = ["电影", "影院", "影视", "院线", "大片", "剧场", "首映", "佳片"]
PAY_KEYS     = ["付费", "高清", "精品", "尊享", "VIP", "点播"]
DIGIT_KEYS   = ["数字", "导视", "测试", "购物", "资讯", "财经", "股市", "数码", "家居"]
PROVINCES    = ["北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
                "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南",
                "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
                "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"]

# ===================== 存储结构 =====================
channels = {
    "央视频道":   set(),
    "卫视频道":   set(),
    "付费频道":   set(),
    "电影频道":   set(),
    "数字频道":   set(),
    "地方频道":   defaultdict(set)
}

# 频道正则
line_re = re.compile(r'([^,#]+?)\s*,\s*(https?://\S+)')

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}")

def get_province(name):
    for p in PROVINCES:
        if p in name:
            return p
    return None

def judge_category(name):
    name = name.strip()
    if any(k in name for k in CCTV_KEYS):
        return "央视频道"
    if any(k in name for k in MOVIE_KEYS):
        return "电影频道"
    if any(k in name for k in PAY_KEYS):
        return "付费频道"
    if any(k in name for k in SAT_KEYS):
        return "卫视频道"
    if any(k in name for k in DIGIT_KEYS):
        return "数字频道"
    if get_province(name):
        return "地方频道"
    return None

def parse_one_url(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        text = r.text
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = line_re.search(line)
            if not match:
                continue
            name, addr = match.groups()
            name = name.strip()
            addr = addr.strip()
            cat = judge_category(name)
            if not cat:
                continue
            if cat == "地方频道":
                prov = get_province(name)
                if prov:
                    channels["地方频道"][prov].add((name, addr))
            else:
                channels[cat].add((name, addr))
        log(f"解析完成: {url}")
    except Exception as e:
        log(f"失败 {url}: {str(e)}")

def main():
    if not os.path.exists(INPUT_FILE):
        log(f"错误：{INPUT_FILE} 不存在")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip()]

    log(f"共加载 {len(urls)} 个源地址，开始解析...")
    for u in urls:
        parse_one_url(u)

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        def write_cat(title, items):
            f.write(f"【{title}】,#genre#\n")
            for n, a in sorted(items):
                f.write(f"{n},{a}\n")
            f.write("\n")

        write_cat("央视频道", channels["央视频道"])
        write_cat("卫视频道", channels["卫视频道"])
        write_cat("付费频道", channels["付费频道"])
        write_cat("电影频道", channels["电影频道"])
        write_cat("数字频道", channels["数字频道"])

        # 地方频道按省份
        for prov in sorted(channels["地方频道"].keys()):
            items = channels["地方频道"][prov]
            write_cat(f"{prov}频道", items)

    log(f"全部完成，结果已保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
