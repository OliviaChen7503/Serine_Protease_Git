#!/usr/bin/env python
import sys
from pymol import cmd
import os

# 检查参数（新增链标识符参数）
if len(sys.argv) != 5:
    print("Usage: python alpha_carbon_rmsd.py <structure_1.pdb> <chain_1> <structure_2.pdb> <chain_2>")
    sys.exit(1)

# 获取参数
structure_1 = sys.argv[1]
chain_1 = sys.argv[2]
structure_2 = sys.argv[3]
chain_2 = sys.argv[4]

# 加载结构
cmd.load(structure_1, "structure_1")
cmd.load(structure_2, "structure_2")

# 选择指定链的α碳原子
cmd.select(f"chain_{chain_1}_1", f"structure_1 and chain {chain_1} and name CA")
cmd.select(f"chain_{chain_2}_2", f"structure_2 and chain {chain_2} and name CA")

# 检查原子选择
if cmd.count_atoms(f"chain_{chain_1}_1") == 0:
    print(f"Error: Chain {chain_1} not found in {structure_1} or contains no CA atoms.")
    sys.exit(1)
if cmd.count_atoms(f"chain_{chain_2}_2") == 0:
    print(f"Error: Chain {chain_2} not found in {structure_2} or contains no CA atoms.")
    sys.exit(1)

# 计算RMSD
rmsd = cmd.align(f"chain_{chain_1}_1", f"chain_{chain_2}_2")[0]

# ======================== 关键修改：生成输出路径 ========================
# 提取文件名（不含路径）
struct1_name = os.path.splitext(os.path.basename(structure_1))[0]
struct2_name = os.path.splitext(os.path.basename(structure_2))[0]

# 生成输出文件名（不含子目录）
output_file = f"{struct1_name}_chain{chain_1}_vs_{struct2_name}_chain{chain_2}_RMSD.txt"

# 写入结果
with open(output_file, "w") as f:
    f.write(f"Structure 1 (Chain {chain_1}): {structure_1}\n")
    f.write(f"Structure 2 (Chain {chain_2}): {structure_2}\n")
    f.write(f"Alpha Carbon RMSD: {rmsd:.3f} Å\n")
