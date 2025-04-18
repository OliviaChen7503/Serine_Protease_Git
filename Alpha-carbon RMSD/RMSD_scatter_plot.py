import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 读取数据（假设CSV已填充空白类别）
df = pd.read_csv("Serine_Protease_Suppmentary_table - Chymotrypsin(pairs).csv")
df["Category"] = df["Category"].fillna(method="ffill")

# 定义颜色映射（可选）
custom_palette = {"#0072B2"
}

# 使用 swarmplot 绘制整齐排列的散点图
plt.figure(figsize=(8, 5))
sns.swarmplot(
    x="Category",
    y="ΔRMSD (Å)",
    data=df,
    palette=custom_palette,  # 指定颜色
    size=7,                  # 点的大小
    edgecolor="black",       # 点边缘颜色
    linewidth=0.5            # 边缘线宽
)

# 优化图表样式
plt.title("Alpha Carbon ΔRMSD Comparison Across Catalytic Cycle for Chymotrypsin", fontsize=13)
plt.ylim(0, 0.2)
plt.grid(axis="y", linestyle="--", alpha=0.5)
sns.despine()
plt.tight_layout()

plt.savefig("rmsd_plot.png", dpi=300)  # 保存高清图
plt.show()
