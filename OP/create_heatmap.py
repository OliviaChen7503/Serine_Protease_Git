import os
import pandas as pd
from functions import generate_op_heatmap, plot_op_distribution, plot_stddev_s2calc

# Read comparison pairs
txt_file = "comparison_pairs_1.csv"
df_pairs = pd.read_csv(txt_file)

# Define the folder containing your merged CSV files
OP_folder = "./"  # Replace with actual path

# Initialize an empty list to store data
data_list = []

# 4. Iterate over GSA and TSA combinations in the TXT file
for _, row in df_pairs.iterrows():
    gsa = row["APO"]
    tsa = row["GSA"]

    # Construct file name
    filename = f"merged_s2calc_diff_{gsa}_{tsa}.csv"
    file_path = os.path.join(OP_folder, filename)

    # Check if file exists
    if os.path.exists(file_path):
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Add PDB ID info
        df['PDB'] = f"{gsa}_{tsa}"

        # Add to the list
        data_list.append(df)
    else:
        print(f"Warning: {filename} not found in {OP_folder}")

# 5. Merge all DataFrames
if data_list:
    OP_df = pd.concat(data_list, ignore_index=True)

    # 6. Run plotting functions
    generate_op_heatmap(OP_df, "heatmap_APO_GSA.png")
    # plot_op_distribution(OP_df, "op_distribution.png")
    # plot_stddev_s2calc(OP_df, "stddev_s2calc.png")

    print("Plots saved as heatmap.png")
else:
    print("No matching files found. No plots generated.")
