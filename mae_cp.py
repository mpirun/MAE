#!/usr/bin/env python
# coding: utf-8

#注意SAXIS=不要有多余空格
import os
import shutil
import math

# 手动选择计算方向，将此处的值修改为 'in' 或 'out'
direction = 'out'

# 定义角度列表
angles = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]

# 复制初始文件的函数
def copy_files(folder):
    os.makedirs(folder, exist_ok=True)
    files_to_copy = ['INCAR', 'POSCAR', 'POTCAR', 'KPOINTS', 'CHGCAR']
    for file in files_to_copy:
        shutil.copy(file, folder)

# 修改 INCAR 文件中 SAXIS 行的函数
def modify_saxis(folder, angle):
    incar_path = os.path.join(folder, 'INCAR')
    with open(incar_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith('SAXIS='):
            if direction == 'in':
                cos_angle = math.cos(math.radians(angle))
                sin_angle = math.sin(math.radians(angle))
                saxis_value = f"SAXIS={cos_angle:.6f} {sin_angle:.6f} 0.000000"
            elif direction == 'out':
                cos_angle = math.cos(math.radians(angle))
                sin_angle = math.sin(math.radians(angle))
                saxis_value = f"SAXIS={cos_angle:.6f} 0.000000 {sin_angle:.6f}"
            new_lines.append(saxis_value + '\n')
        else:
            new_lines.append(line)

    with open(incar_path, 'w') as f:
        f.writelines(new_lines)

# 运行 VASP 计算的函数
def run_vasp(folder):
    os.chdir(folder)
    command = "nohup mpirun -n 20 vasp_ncl > log &"
    os.system(command)
    # 等待计算完成
    while True:
        if os.path.exists('OSZICAR'):
            with open('OSZICAR', 'r') as f:
                content = f.read()
                if 'F=' in content:
                    break
    os.chdir('..')

# 循环处理每个角度
for angle in angles:
    folder = f"{direction}_{angle}"
    copy_files(folder)
    modify_saxis(folder, angle)
    run_vasp(folder)




