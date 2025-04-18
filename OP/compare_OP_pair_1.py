import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Define catalytic residues
catalytic_residues = [57, 102, 195]

# Load the distance data
distance_data = pd.read_csv("1QNJ_qFit_all_distances.csv")

# Function to classify residues based on distance
def classify_residue(residue_num, distance_data, catalytic_residues):
    # Check if residue is catalytic
    if residue_num in catalytic_residues:
        return "Catalytic"
    
    # Get the distance for the residue
    distance_row = distance_data[distance_data["resi"] == residue_num]
    if not distance_row.empty:
        distance = distance_row["distance"].values[0]
        
        # Classify based on distance
        if distance < 4:
            return "Binding"
        elif distance > 10:
            return "Distal"
        else:
            return "Other"
    else:
        return "Unknown"

# Function to read OP.out files from the specified directory
def read_op_file(pdb_id, directory):
    pdb_file = os.path.join(directory, f"{pdb_id}_OP.out")
    if os.path.exists(pdb_file):
        return pd.read_csv(pdb_file)
    else:
        print(f"Warning: File {pdb_file} not found!")
        return None

# Read the comparison pairs file (PDB1, PDB2)
comparison_data = pd.read_csv("comparison_pairs_1.csv")  # Replace with your actual comparison file

# Initialize a list to store all ΔS² values and their categories
all_s2calc_diff = []
all_categories = []

# Specify the directory containing the OP.out files
directory = "OP_df"  # Replace with your directory path

# Loop through each comparison pair
for index, row in comparison_data.iterrows():
    pdb1 = row['GSA']
    chain1 = row['Chain']
    pdb2 = row['TSA']
    chain2 = row['Chain.1']

    # Read the two OP.out files corresponding to the current comparison
    pdb1_df = read_op_file(pdb1, directory)
    pdb2_df = read_op_file(pdb2, directory)
    
    if pdb1_df is not None and pdb2_df is not None:
        # Merge data on residue and chain to compute ΔS²
        merged = pd.merge(
            pdb1_df[["resi", "chain", "s2calc"]],
            pdb2_df[["resi", "chain", "s2calc"]],
            on=["resi", "chain"],
            suffixes=("_pdb1", "_pdb2"),
        )
        
        # Calculate ΔS²
        merged["s2calc_diff"] = merged["s2calc_pdb2"] - merged["s2calc_pdb1"]
        
        # Classify residues based on distance from catalytic residues
        merged["category"] = merged["resi"].apply(lambda x: classify_residue(x, distance_data, catalytic_residues))
        
        # Append the ΔS² differences and categories to the lists
        all_s2calc_diff.extend(merged["s2calc_diff"])
        all_categories.extend(merged["category"])

        # Output the merged DataFrame (with s2calc_diff and categories) to CSV after this step
        merged.to_csv(f"merged_s2calc_diff_{pdb1}_{pdb2}.csv", index=False)

# Combine all results into a DataFrame for the final output
final_df = pd.DataFrame({
    "s2calc_diff": all_s2calc_diff,
    "category": all_categories
})

# Plot KDE of ΔS² for all comparisons, categorized
plt.figure(figsize=(8, 6))

# Plot KDE for each category with different colors
for category, color in zip(["Catalytic", "Binding", "Distal"], ["red", "green", "blue"]):
    sns.kdeplot(
        data=final_df[final_df["category"] == category], 
        x="s2calc_diff", 
        fill=True, 
        color=color, 
        alpha=0.5,
        label=category
    )

plt.xlabel("ΔS² (TSA-GSA)", fontsize=12)
plt.ylabel("Density", fontsize=12)
plt.title("ΔS² Distribution for GSA vs. TSA", fontsize=14)
plt.legend(title="Residue Categories")
plt.grid(linestyle="--", alpha=0.3)
plt.savefig("ΔOP_distribution_GSA_TSA.png", dpi=300)
plt.close()

# Save the final results (ΔS² and categories) to a CSV file
final_df.to_csv("ΔOP_GSA_TSA.csv", index=False)

