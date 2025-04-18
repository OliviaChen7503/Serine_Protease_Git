import pandas as pd
import matplotlib.pyplot as plt

# 读取数据（注意文件名中的空格和特殊字符）
file_path = "Serine_Protease_Suppmentary_table - Chymotrypsin(filtered).csv"
df = pd.read_csv(file_path)

# 提取并清洗 R_free 列数据
r_free = pd.to_numeric(df["R_free"], errors="coerce").dropna()

# 绘制直方图
plt.figure(figsize=(10, 6))
plt.hist(r_free,
         bins=18,                    # 根据数据范围优化
         range=(0.14, 0.26),         # 基于数据样本的观察范围
         color="#0072B2",            # 科学配色
         edgecolor="black",
         alpha=0.8,
         density=False)              # 显示频次而非密度

# 图表标注
plt.title("R_free Distribution of Chymotrpsin Structures", fontsize=14, pad=20)
plt.xlabel("R_free Value", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(axis="y", linestyle=":", alpha=0.4)

# 添加统计信息
stats_text = f"""Dataset Summary:
Total entries: {len(r_free):d}
Mean: {r_free.mean():.3f}
Median: {r_free.median():.3f}
Min: {r_free.min():.3f}
Max: {r_free.max():.3f}
Std Dev: {r_free.std():.3f}"""
plt.text(0.95, 0.95, stats_text,
         transform=plt.gca().transAxes,
         ha="right", va="top",
         fontsize=10,
         bbox=dict(facecolor="white", edgecolor="grey", boxstyle="round,pad=0.3"))

# 优化布局并保存
plt.tight_layout()
plt.savefig("Elastase_R_free_Distribution.png", dpi=300, bbox_inches="tight")
plt.show()
