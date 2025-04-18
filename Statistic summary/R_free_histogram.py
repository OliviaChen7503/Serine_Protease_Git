import pandas as pd
import matplotlib.pyplot as plt

# Read data (note the spaces and special characters in the filename)
file_path = "Serine_Protease_Suppmentary_table - Chymotrypsin(filtered).csv"
df = pd.read_csv(file_path)

# Extract and clean R_free column data
r_free = pd.to_numeric(df["R_free"], errors="coerce").dropna()

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(r_free,
         bins=18,                    # Optimized based on data range
         range=(0.14, 0.26),         # Observed range from data sample
         color="#0072B2",            # Scientific color palette
         edgecolor="black",
         alpha=0.8,
         density=False)              # Show frequency instead of density

# Add chart labels
plt.title("R_free Distribution of Chymotrpsin Structures", fontsize=14, pad=20)
plt.xlabel("R_free Value", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(axis="y", linestyle=":", alpha=0.4)

# Add summary statistics
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

# Optimize layout and save figure
plt.tight_layout()
plt.savefig("Elastase_R_free_Distribution.png", dpi=300, bbox_inches="tight")
plt.show()
