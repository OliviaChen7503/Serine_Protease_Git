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

# 4. 遍历 TXT 文件中的 GSA 和 TSA 组合
for _, row in df_pairs.iterrows():
    gsa = row["APO"]
    tsa = row["GSA"]

    # 构造文件名
    filename = f"merged_s2calc_diff_{gsa}_{tsa}.csv"
    file_path = os.path.join(OP_folder, filename)

    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 添加 PDB ID 信息
        df['PDB'] = f"{gsa}_{tsa}"

        # 添加到列表
        data_list.append(df)
    else:
        print(f"Warning: {filename} not found in {OP_folder}")

# 5. 合并所有 DataFrame
if data_list:
    OP_df = pd.concat(data_list, ignore_index=True)

    # 6. 运行绘图函数
    generate_op_heatmap(OP_df, "heatmap_APO_GSA.png")
    # plot_op_distribution(OP_df, "op_distribution.png")
    # plot_stddev_s2calc(OP_df, "stddev_s2calc.png")

    print("Plots saved as heatmap.png")
else:
    print("No matching files found. No plots generated.")

