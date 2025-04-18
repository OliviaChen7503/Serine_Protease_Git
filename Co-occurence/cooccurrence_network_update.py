import Bio.PDB
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import glob
import os

# ---------- 新增函数：生成唯一残基标识 ----------
def get_residue_id(res):
    """生成包含插入码的唯一残基标识符（格式：残基名+序列号+插入码）"""
    seqnum = res.get_id()[1]
    icode = res.get_id()[2].strip()  # 获取插入码并去除空格
    return f"{res.get_resname()}{seqnum}{icode}"

# ---------- 修改后的核心函数 ----------
def compute_cooccurrence_multi(structures, distance_threshold=4.0):
    cooccurrence = {}

    for structure in structures:
        model = structure[0]
        residues = list(model.get_residues())
        seen_pairs = set()  # 记录当前结构已处理的残基对

        for i, res1 in enumerate(residues):
            for j, res2 in enumerate(residues):
                if i >= j:
                    continue  # 避免重复对(i,j)和(j,i)

                # 生成唯一键（排序后保证顺序无关）
                pair_key = tuple(sorted([get_residue_id(res1), get_residue_id(res2)]))
                
                # 跳过已处理的残基对
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                # 计算非氢原子间最小距离
                min_dist = min(
                    (atom1 - atom2 for atom1 in res1 if atom1.element != 'H'
                     for atom2 in res2 if atom2.element != 'H'),
                    default=float('inf')  # 若无原子对，设距离为无穷大
                )

                # 满足距离阈值则计数
                if min_dist <= distance_threshold:
                    cooccurrence[pair_key] = cooccurrence.get(pair_key, 0) + 1

    return cooccurrence

# ---------- 其余函数保持不变 ----------
def load_structures(pdb_files):
    parser = Bio.PDB.PDBParser(QUIET=True)
    return [parser.get_structure(f"protein_{i}", file) for i, file in enumerate(pdb_files)]

def normalize_cooccurrence(cooccurrence, num_structures):
    return {pair: count / num_structures for pair, count in cooccurrence.items()}

def build_network(cooccurrence):
    G = nx.Graph()
    for (res1, res2), freq in cooccurrence.items():
        G.add_edge(res1, res2, weight=freq)
    return G

def plot_network(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    edges = G.edges(data=True)
    edge_weights = [data["weight"] for _, _, data in edges]

    nx.draw(G, pos, with_labels=True, 
            node_color="skyblue", 
            edge_color=edge_weights,
            edge_cmap=plt.cm.Blues, 
            node_size=500, 
            font_size=10, 
            width=2)

    plt.savefig("TSA_residue_network.png", dpi=300) ################NEED CHANGE################
    
    # 保存权重到CSV
    edge_df = pd.DataFrame(
        [(res1, res2, data["weight"]) for res1, res2, data in G.edges(data=True)],
        columns=["Residue1", "Residue2", "Weight"]
    )
    edge_df.to_csv("TSA_residue_network_weights.csv", index=False) ##############NEED CHANGE###############

# ---------- 主流程 ----------
if __name__ == "__main__":
    # 加载PDB文件（示例路径，需根据实际情况修改）
    pdb_files = glob.glob("/dors/wankowicz_lab/serine_protease/Chymotrypsin/TSA/*.pdb")[:3] ##########NEED CHANGE#########
    print(f"Processing {len(pdb_files)} PDB files:")
    for f in pdb_files:
        print(" -", os.path.basename(f))
    
    structures = load_structures(pdb_files)
    
    # 计算共现并归一化
    cooccurrence = compute_cooccurrence_multi(structures)
    normalized_cooccurrence = normalize_cooccurrence(cooccurrence, len(pdb_files))
    
    # 验证最大权重是否≤1
    max_weight = max(normalized_cooccurrence.values()) if normalized_cooccurrence else 0
    print(f"\n验证结果：最大权重值 = {max_weight:.2f} (应≤1.0)\n")
    
    # 构建网络并输出
    G = build_network(normalized_cooccurrence)
    plot_network(G)
