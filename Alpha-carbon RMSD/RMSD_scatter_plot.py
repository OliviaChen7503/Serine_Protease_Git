import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read data (assume missing categories in CSV are already filled downward)
df = pd.read_csv("Serine_Protease_Suppmentary_table - Chymotrypsin(pairs).csv")
df["Category"] = df["Category"].fillna(method="ffill")

# Define custom color palette (optional)
custom_palette = {"#0072B2"}

# Plot tidy scatter using swarmplot
plt.figure(figsize=(8, 5))
sns.swarmplot(
    x="Category",
    y="ΔRMSD (Å)",
    data=df,
    palette=custom_palette,  # Specify color
    size=7,                  # Dot size
    edgecolor="black",       # Dot edge color
    linewidth=0.5            # Edge line width
)

# Improve plot aesthetics
plt.title("Alpha Carbon ΔRMSD Comparison Across Catalytic Cycle for Chymotrypsin", fontsize=13)
plt.ylim(0, 0.2)
plt.grid(axis="y", linestyle="--", alpha=0.5)
sns.despine()
plt.tight_layout()

plt.savefig("rmsd_plot.png", dpi=300)  # Save high-resolution image
plt.show()
