#!/usr/bin/env python
# coding: utf-8

import os
import re
import matplotlib.pyplot as plt
import numpy as np

# 手动输入元素分组信息和规定值
group_info = [6, 2, 2]
target_value = -3.6

# 设置全局绘图参数，使用罗马字体
plt.rcParams.update({
    'font.family':'serif',
    'figure.dpi': 300,
    'figure.figsize': (5, 4),
    'axes.titlesize': 18,  # 增大标题字体大小
    'xtick.labelsize': 14,  # 增大 x 轴刻度字体大小
    'ytick.labelsize': 14,  # 增大 y 轴刻度字体大小
    'axes.linewidth': 1.5,
    'axes.labelsize': 16  # 增大轴标签字体大小
})


def extract_content(file_path):
    """提取指定路径OUTCAR文件中SOC到total charge的内容"""
    extracted = []
    try:
        with open(file_path, 'r') as f:
            start_flag = False
            line_num = 0
            for line in f:
                line_num += 1
                if 'Spin-Orbit-Coupling matrix elements' in line:
                    start_flag = True
                    extracted.append(line)
                elif start_flag:
                    if 'total charge' in line:
                        break
                    extracted.append(line)
            if not start_flag:
                print(f"未找到起始标志 'Spin-Orbit-Coupling matrix elements' 在文件 {file_path} 中。")
            return extracted
    except FileNotFoundError:
        print(f"未找到文件：{file_path}")
        return []
    except Exception as e:
        print(f"读取文件 {file_path} 时发生未知错误，错误信息：{e}，在第 {line_num} 行。")
        return []


def process_folders(in_folder, out_folder):
    """处理两个文件夹并生成差值文件"""
    # 提取内容
    in_content = extract_content(os.path.join(in_folder, 'OUTCAR'))
    out_content = extract_content(os.path.join(out_folder, 'OUTCAR'))

    if not in_content or not out_content:
        print("内容提取失败，请检查文件")
        return

    # 逐行处理并计算差值
    diff_content = []
    e_soc_diffs = []
    for in_line, out_line in zip(in_content, out_content):
        if 'Ion:' in in_line and 'E_soc:' in in_line:
            # 修正正则匹配，确保匹配多个空格
            match_in = re.search(r'Ion:\s+(\d+)\s+E_soc:\s+([-+]?\d*\.\d+)', in_line)
            match_out = re.search(r'Ion:\s+(\d+)\s+E_soc:\s+([-+]?\d*\.\d+)', out_line)

            if match_in and match_out:
                ion_number = match_in.group(1)  # 提取 Ion 号
                in_E_soc = float(match_in.group(2))
                out_E_soc = float(match_out.group(2))
                diff_E_soc = in_E_soc - out_E_soc
                new_line = f"Ion: {ion_number}  E_soc: {diff_E_soc:12.7f}\n"
                print(f"解析成功: {in_line.strip()} - {out_line.strip()} = {new_line.strip()}")  # 调试信息
                e_soc_diffs.append(diff_E_soc)
            else:
                print(f"解析失败: {in_line.strip()} 或 {out_line.strip()}")  # 调试信息
                new_line = in_line  # 解析失败时保留原内容
            diff_content.append(new_line)

        elif in_line.startswith(('l= ', 'Spin-Orbit-Coupling matrix elements')):
            diff_content.append(in_line)

        else:
            # 处理数值矩阵行
            try:
                in_values = list(map(float, in_line.split()))
                out_values = list(map(float, out_line.split()))
                diff_values = [i - o for i, o in zip(in_values, out_values)]
                formatted = ['%12.7f' % val for val in diff_values]
                new_line = ''.join(formatted).rstrip() + '\n'
                diff_content.append(new_line)
            except:
                diff_content.append(in_line)  # 直接保留非数值行

    # 保存结果
    with open('orbital_contribution.txt', 'w') as f:
        f.writelines(diff_content)
    print("差值文件已生成：orbital_contribution.txt")

    # 计算每组平均值
    group_averages = []
    start_index = 0
    for group_size in group_info:
        group = e_soc_diffs[start_index:start_index + group_size]
        average = sum(group) / len(group)
        group_averages.append(average)
        start_index += group_size

    # 计算比例系数 x
    sum_of_averages = sum(group_averages)
    x = target_value / sum_of_averages

    # 计算每组乘以比例系数后的值
    group_results = [avg * x for avg in group_averages]

    # 生成新的 txt 文件
    with open('element_results.txt', 'w') as f:
        f.write("Element\tValue\n")
        for i, result in enumerate(group_results, 1):
            f.write(f"Element {i}\t{result:.7f}\n")
    print("元素结果文件已生成：element_results.txt")

    # 绘制柱状图
    elements = [f'Element {i}' for i in range(1, len(group_results) + 1)]
    plt.figure()
    bar_colors = []
    for result in group_results:
        if result >= 0:
            bar_colors.append('C0')
        else:
            bar_colors.append('C1')
    bars = plt.bar(elements, group_results, color=bar_colors)

    # 添加数据标签
    label_values = []
    for bar in bars:
        height = bar.get_height()
        if height >= 0:
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.05 * abs(height),
                     f'{height:.3f}', ha='center', va='bottom')
        else:
            plt.text(bar.get_x() + bar.get_width() / 2, height - 0.05 * abs(height),
                     f'{height:.3f}', ha='center', va='top')
        label_values.append(height)

    # 调整 y 轴范围以确保标签不超出图框
    max_label = max(label_values)
    min_label = min(label_values)
    padding = 0.1 * (max_label - min_label) if max_label != min_label else 0.1
    plt.ylim(min_label - padding, max_label + padding)

    # 设置标题和坐标轴标签
    plt.title('Element Value Bar Chart')
    plt.xlabel('Element')
    plt.ylabel('Value')

    # 自动调整布局以确保标题显示完整
    plt.tight_layout()

    # 保存图片
    img_filename = 'element.png'
    plt.savefig(img_filename)
    print(f"成功生成{img_filename}")

    # 显示图形
    plt.show()


if __name__ == "__main__":
    process_folders('in_90', 'out_90')
    
