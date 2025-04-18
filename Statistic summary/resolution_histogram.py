import pandas as pd
import matplotlib.pyplot as plt

# Read CSV data (assumes file is in current directory)
df = pd.read_csv("Serine_Protease_Raw_data1.csv")

# Extract and clean resolution column (ensure numeric values)
resolution = pd.to_numeric(df["Resolution (Å)"], errors="coerce").dropna()

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(resolution, bins=30, color="#999999", edgecolor="black", alpha=0.8)

# Add labels
plt.title("Resolution Distribution of Serine Protease Structures", fontsize=14)
plt.xlabel("Resolution (Å)", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.4)

# Add statistical summary text
stats_text = f"""
Total entries: {len(resolution):,}
Mean: {resolution.mean():.2f} Å
Median: {resolution.median():.2f} Å
Min: {resolution.min():.2f} Å
Max: {resolution.max():.2f} Å
"""
plt.text(0.95, 0.95, stats_text,
         transform=plt.gca().transAxes,
         ha="right", va="top",
         bbox=dict(facecolor="white", edgecolor="gray", boxstyle="round"))

# Save figure
plt.tight_layout()
plt.savefig("resolution_distribution.png", dpi=300)
plt.show()
