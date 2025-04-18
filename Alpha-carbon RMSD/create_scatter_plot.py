import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read CSV file
file_path = "Alpha_Lytic_Protease_pairs.csv"
df = pd.read_csv(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Detect columns dynamically
category_col = next((col for col in df.columns if "category" in col.lower()), None)
rmsd_col = next((col for col in df.columns if "rmsd" in col.lower()), None)

# Ensure both columns were found
if category_col is None or rmsd_col is None:
    raise ValueError("Could not find 'Category' or 'RMSD' columns. Check column names.")

# Forward-fill missing category values
df[category_col] = df[category_col].fillna(method="ffill")

# Drop missing values in detected columns
df = df.dropna(subset=[category_col, rmsd_col])

# Set plot style
sns.set_style("whitegrid")

# Create scatter plot
plt.figure(figsize=(8, 5))
sns.stripplot(x=category_col, y=rmsd_col, data=df, jitter=False, size=8, alpha=0.7)

# Add labels and title
plt.xlabel(category_col)
plt.ylabel(rmsd_col)
plt.title("Scatter Plot of ΔRMSD for Alpha Lytic Protease")
plt.xticks(rotation=30)  # Rotate x-axis labels for better readability

# Save plot as a file
output_file = "scatter_plot.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")

print(f"Plot saved as {output_file}")

