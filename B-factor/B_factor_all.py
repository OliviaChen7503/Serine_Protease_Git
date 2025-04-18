import MDAnalysis as mda
import numpy as np
import matplotlib.pyplot as plt

# 文件名列表
pdb_files = ["2GCH/2GCH.updated_refine_001_ensemble.pdb", "1AFQ/1AFQ.updated_refine_001_ensemble.pdb", "3VGC/3VGC.updated_refine_001_ensemble.pdb"]
labels = ["2GCH(APO)", "1AFQ(GSA)", "3VGC(TSA)"]
colors = ["r", "g", "b"]

# 存储所有模型的 B-factor
bfactors_all = []

for pdb in pdb_files:
    u = mda.Universe(pdb)
    ca = u.select_atoms("name CA")  # 只选Cα原子
    bfactors = ca.tempfactors
    bfactors_all.append(bfactors)

# 确保所有长度一致
min_len = min(len(b) for b in bfactors_all)
bfactors_all = [b[:min_len] for b in bfactors_all]  # 截断到最短长度

# 绘图
residue_indices = np.arange(1, min_len + 1)
plt.figure(figsize=(12, 6))

for bfactors, label, color in zip(bfactors_all, labels, colors):
    plt.plot(residue_indices, bfactors, label=label, color=color, linewidth=2)

plt.xlabel("Residue Index (Cα)")
plt.ylabel("B-factor")
plt.title("Comparison of B-factors across Models")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("bfactor_comparison.png", dpi=300)
plt.show()

