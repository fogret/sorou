# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

def parse_and_deduplicate(data_file="data.txt", output_file="fenl_output.txt"):
    # 日志文件（仅记录执行状态，不包含任何敏感信息）
    log_file = "run_log.txt"

    def log_message(message):
        """写入运行日志到 run_log.txt"""
        with open(log_file, "a", encoding="utf-8") as f_log:
            f_log.write(message + "\n")

    try:
        # 初始化日志
        if not os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== 运行日志开始 ===\n")

        log_message("开始执行解析任务")

        # 校验输入文件
        if not os.path.exists(data_file):
            error_msg = f"错误：未找到文件 {data_file}"
            log_message(error_msg)
            print(error_msg)
            return

        # 存储结果：key=分类名，value=去重后的频道名列表
        result = OrderedDict()
        processed_channels = set()  # 用于去重

        # 读取并解析数据
        with open(data_file, "r", encoding="utf-8") as f_data:
            for line_num, line_content in enumerate(f_data, 1):
                line = line_content.strip()
                if not line:
                    continue  # 跳过空行

                # 解析格式：分类名|频道名|播放链接
                parts = line.split("|")
                if len(parts) >= 3:
                    category = parts[0].strip()
                    channel_name = parts[1].strip()
                    # 忽略播放链接（只保留分类名和频道名）

                    if category and channel_name:
                        if category not in result:
                            result[category] = OrderedDict()
                        # 去重处理
                        if channel_name not in processed_channels:
                            processed_channels.add(channel_name)
                            result[category][channel_name] = True

        # 写入最终结果
        with open(output_file, "w", encoding="utf-8") as f_out:
            for category, channel_dict in result.items():
                # 按分类排序，保证输出有序
                sorted_channels = sorted(channel_dict.keys())
                f_out.write(f"{category}:\n")
                for channel in sorted_channels:
                    f_out.write(f"  {channel}\n")
                f_out.write("\n")  # 分类间空一行，便于阅读

        success_msg = f"解析完成！结果已写入 {output_file}，共处理 {len(processed_channels)} 个频道"
        log_message(success_msg)
        print(success_msg)

    except Exception as e:
        error_msg = f"执行失败：{str(e)}"
        log_message(error_msg)
        print(error_msg)

if __name__ == "__main__":
    # 可直接修改输入/输出文件名
    parse_and_deduplicate(data_file="data.txt", output_file="fenl_output.txt")
