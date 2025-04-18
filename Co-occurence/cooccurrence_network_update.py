import Bio.PDB
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import glob
import os


# ---------- New function: generate unique residue identifier ----------
def get_residue_id(res):
    """Generate a unique residue ID including insertion code (format: resname + seq number + icode)"""
    seqnum = res.get_id()[1]
    icode = res.get_id()[2].strip()  # Get insertion code and strip whitespace
    return f"{res.get_resname()}{seqnum}{icode}"


# ---------- Modified core function ----------
def compute_cooccurrence_multi(structures, distance_threshold=4.0):
    cooccurrence = {}

    for structure in structures:
        model = structure[0]
        residues = list(model.get_residues())
        seen_pairs = set()  # Record processed residue pairs for current structure

        for i, res1 in enumerate(residues):
            for j, res2 in enumerate(residues):
                if i >= j:
                    continue  # Skip duplicates (i,j) and (j,i)

                # Generate sorted key to ensure pair order independence
                pair_key = tuple(sorted([get_residue_id(res1), get_residue_id(res2)]))

                # Skip if pair already processed
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                # Compute minimal distance between heavy atoms
                min_dist = min(
                    (atom1 - atom2 for atom1 in res1 if atom1.element != 'H'
                     for atom2 in res2 if atom2.element != 'H'),
                    default=float('inf')  # If no atom pairs, set to infinity
                )

                # Count if within threshold
                if min_dist <= distance_threshold:
                    cooccurrence[pair_key] = cooccurrence.get(pair_key, 0) + 1

    return cooccurrence


# ---------- Remaining functions unchanged ----------
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

    plt.savefig("TSA_residue_network.png", dpi=300)  ################NEED CHANGE################

    # Save weights to CSV
    edge_df = pd.DataFrame(
        [(res1, res2, data["weight"]) for res1, res2, data in G.edges(data=True)],
        columns=["Residue1", "Residue2", "Weight"]
    )
    edge_df.to_csv("TSA_residue_network_weights.csv", index=False)  ##############NEED CHANGE###############


# ---------- Main pipeline ----------
if __name__ == "__main__":
    # Load PDB files (example path; modify as needed)
    pdb_files = glob.glob("/dors/wankowicz_lab/serine_protease/Chymotrypsin/TSA/*.pdb")[
                :3]  ##########NEED CHANGE#########
    print(f"Processing {len(pdb_files)} PDB files:")
    for f in pdb_files:
        print(" -", os.path.basename(f))

    structures = load_structures(pdb_files)

    # Compute and normalize co-occurrence
    cooccurrence = compute_cooccurrence_multi(structures)
    normalized_cooccurrence = normalize_cooccurrence(cooccurrence, len(pdb_files))

    # Check if max weight ≤ 1
    max_weight = max(normalized_cooccurrence.values()) if normalized_cooccurrence else 0
    print(f"\nValidation: max weight = {max_weight:.2f} (should be ≤ 1.0)\n")

    # Build network and output
    G = build_network(normalized_cooccurrence)
    plot_network(G)
