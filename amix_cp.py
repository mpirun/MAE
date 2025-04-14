#!/usr/bin/env python
# coding: utf-8
import os
import shutil
import subprocess
import numpy as np  # 导入 numpy 库

# 定义 AMIX 参数范围
amix_values = [round(val, 2) for val in np.arange(0.5, 0.7, 0.04)] # 0.02 到 0.2，每隔 0.02

# 当前目录
base_dir = os.getcwd()

# 输入文件
input_files = ["INCAR", "POSCAR", "POTCAR", "KPOINTS"]

# VASP 运行命令（无 nohup，确保同步执行）
vasp_command = "mpirun -n 20 vasp_ncl > log"

# 检查输入文件是否存在
for file in input_files:
    if not os.path.isfile(file):
        print(f"Error: {file} not found in the current directory!")
        exit(1)

# 遍历 AMIX 参数
for amix in amix_values:
    # 创建新的目录
    folder_name = f"run_AMIX_{amix}"
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # 复制输入文件到新目录
    for file in input_files:
        shutil.copy(os.path.join(base_dir, file), folder_path)

    # 修改 INCAR 文件的 AMIX 参数
    incar_path = os.path.join(folder_path, "INCAR")
    with open(incar_path, "r") as f:
        incar_lines = f.readlines()

    with open(incar_path, "w") as f:
        for line in incar_lines:
            if line.strip().startswith("AMIX"):
                f.write(f"AMIX = {amix}\n")
            else:
                f.write(line)

    # 切换到新目录并运行 VASP
    os.chdir(folder_path)
    print(f"Running VASP with AMIX = {amix} in {folder_name}...")

    # 同步运行 VASP，等待任务完成
    result = subprocess.run(vasp_command, shell=True)

    # 检查运行结果
    if result.returncode == 0:
        print(f"Calculation for AMIX = {amix} completed successfully.")
    else:
        print(f"Error: Calculation for AMIX = {amix} failed.")
        break  # 如果出错，停止后续任务

    # 返回初始目录
    os.chdir(base_dir)

print("All calculations completed.")




