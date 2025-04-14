#!/usr/bin/env python
# coding: utf-8
import os
import re
import matplotlib.pyplot as plt

import numpy as np  # 导入 numpy 库

# 定义 AMIX 参数范围
amix_values = [round(val, 2) for val in np.arange(0.4, 0.61, 0.02)] # 0.02 到 0.2，每隔 0.02

# 当前目录
base_dir = os.getcwd()

# 用于保存 AMIX 和 GAMMA 值的列表
amix_gamma_pairs = []

# 遍历 AMIX 参数文件夹
for amix in amix_values:
    folder_name = f"run_AMIX_{amix}"
    folder_path = os.path.join(base_dir, folder_name)

    if os.path.isdir(folder_path):
        outcar_path = os.path.join(folder_path, "OUTCAR")

        # 检查 OUTCAR 文件是否存在
        if os.path.isfile(outcar_path):
            try:
                # 从 OUTCAR 中提取最后一个 GAMMA 值
                with open(outcar_path, "r") as f:
                    outcar_lines = f.readlines()

                # 使用正则表达式提取 GAMMA 值
                gamma_values = []
                for line in outcar_lines:
                    match = re.search(r"average eigenvalue GAMMA=\s*([\d\.\-]+)", line)
                    if match:
                        gamma_values.append(float(match.group(1)))

                # 取最后一个 GAMMA 值
                if gamma_values:
                    gamma_last = gamma_values[-1]
                    amix_gamma_pairs.append((amix, gamma_last))
 #                   print(f"GAMMA for AMIX = {amix}: {gamma_last}")
                else:
                    print(f"Warning: No GAMMA values found in OUTCAR for AMIX = {amix}")

            except Exception as e:
                print(f"Error reading OUTCAR for AMIX = {amix}: {e}")

# 如果有有效的 AMIX 和 GAMMA 值，进行绘图
if amix_gamma_pairs:
    amix_values, gamma_values = zip(*amix_gamma_pairs)  # 解压元组为两个列表
    plt.figure(figsize=(5, 4))  # 设置图像大小

    # 绘制 AMIX vs GAMMA 图
    plt.plot(amix_values, gamma_values, marker='o', linestyle='-', color='b', markersize=8, label='GAMMA vs AMIX')

    # 设置坐标轴标签和标题
    plt.xlabel('AMIX', fontsize=14)
    plt.ylabel('GAMMA', fontsize=14)
    plt.title('AMIX vs GAMMA', fontsize=16)

    # 设置网格
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 设置坐标轴范围
    plt.xlim(min(amix_values) - 0.01, max(amix_values) + 0.01)
    plt.ylim(min(gamma_values) - 0.1, max(gamma_values) + 0.1)

    # 设置 x 轴的刻度，以匹配 amix_values
    plt.xticks(amix_values)

    # 显示图例
    plt.legend(fontsize=12)

    # 添加红色水平线 y = 1
    plt.axhline(y=1, color='r', linestyle='--', label='y = 1')

    # 添加标注，显示每个点的值
    for i, txt in enumerate(gamma_values):
        plt.annotate(f'{txt:.2f}', (amix_values[i], gamma_values[i]), textcoords="offset points", xytext=(0, 5), ha='center')



    # 保存为图片文件
    output_image_path = "amix_vs_gamma.png"
    plt.savefig(output_image_path, dpi=600)
    print(f"Plot saved as {output_image_path}")



else:
    print("No valid GAMMA data found.")
