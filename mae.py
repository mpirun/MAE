#!/usr/bin/env python
# coding: utf-8

import os
import subprocess
import matplotlib.pyplot as plt

# 定义角度列表
angles = [0, 15, 30, 45, 60, 75,90, 105, 120, 135, 150, 165,180]

# 定义常数 x
x = 2

# 设置字体
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# 函数用于从 OUTCAR 文件中提取能量值
def get_energy(folder):
    outcar_path = os.path.join(folder, 'OUTCAR')
    if os.path.exists(outcar_path):
        try:
            command = f"grep TOTEN {outcar_path} | tail -1"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout.strip()
            if output:
                energy = float(output.split()[-2])
                return energy
        except Exception as e:
            print(f"Error getting energy from {folder}: {e}")
    return None

# 获取 out_90 的能量值
out_90_energy = get_energy('out_90')
if out_90_energy is None:
    print("Error: Could not get energy from out_90.")
    exit(1)

# 处理 in 文件夹
in_energies = []
for angle in angles:
    folder = f"in_{angle}"
    energy = get_energy(folder)
    if energy is not None:
        in_energies.append(energy)
    else:
        in_energies.append(None)

# 处理 out 文件夹
out_energies = []
for angle in angles:
    folder = f"out_{angle}"
    energy = get_energy(folder)
    if energy is not None:
        out_energies.append(energy)
    else:
        out_energies.append(None)

# 处理 in 能量数据：减去 out_90 的能量值并除以 x，再乘以 1000 转换为 meV
in_energies = [(energy - out_90_energy) / x * 1000 if energy is not None else None for energy in in_energies]

# 处理 out 能量数据：减去 out_90 的能量值并除以 x，再乘以 1000 转换为 meV
out_energies = [(energy - out_90_energy) / x * 1000 if energy is not None else None for energy in out_energies]

# 保存 in 数据到文件
with open('in_energy_data.txt', 'w') as f:
    f.write("Angle (degrees)\tEnergy (meV)\n")
    for angle, energy in zip(angles, in_energies):
        if energy is not None:
            f.write(f"{angle}\t{energy}\n")

# 保存 out 数据到文件
with open('out_energy_data.txt', 'w') as f:
    f.write("Angle (degrees)\tEnergy (meV)\n")
    for angle, energy in zip(angles, out_energies):
        if energy is not None:
            f.write(f"{angle}\t{energy}\n")

# 设置绘图参数
plt.rcParams['figure.figsize'] = (4, 3.3)  # 图大小
plt.rcParams['axes.linewidth'] = 1.5  # 边框粗细
plt.rcParams['axes.titlesize'] = 16  # 标题字体大小
plt.rcParams['xtick.labelsize'] = 12  # 刻度字体大小
plt.rcParams['ytick.labelsize'] = 12  # 刻度字体大小
plt.rcParams['axes.labelsize'] = 14
# 绘制点线图
plt.figure()

# 绘制 in 数据
valid_in_angles = [angle for angle, energy in zip(angles, in_energies) if energy is not None]
valid_in_energies = [energy for energy in in_energies if energy is not None]
plt.plot(valid_in_angles, valid_in_energies, marker='o', markersize=7, color='g', label='in')

# 绘制 out 数据
valid_out_angles = [angle for angle, energy in zip(angles, out_energies) if energy is not None]
valid_out_energies = [energy for energy in out_energies if energy is not None]
plt.plot(valid_out_angles, valid_out_energies, marker='o', markersize=7, color='C0', label='out')

# 设置横坐标刻度为 0, 30, 60, ..., 180
plt.xticks([i for i in range(0, 181, 30)])

plt.xlabel('Rotation degree')
plt.ylabel('MAE (meV)')
#plt.title('Energy vs Angle')

# 图例放中间
plt.legend(loc='center')

plt.grid(True)
plt.tight_layout()

# 输出 300dpi 图片
plt.savefig('MAE.png', dpi=300)
print("检查是否归一化！")
print("成功输出图片MAE.png")
plt.show()    
