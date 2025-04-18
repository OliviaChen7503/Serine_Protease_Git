from Bio.PDB import PDBParser
import numpy as np
import matplotlib.pyplot as plt

p = PDBParser(QUIET=True)
structure = p.get_structure("ensemble", "2GCH/2GCH.updated_refine_001_ensemble.pdb")

res_b_factors = {}

for model in structure:
    for chain in model:
        if chain.id == 'S':  # ⛔️ Skip chain S entirely
            continue
        for residue in chain:
            if residue.id[0] != ' ':
                continue  # Skip HETATM (e.g., water, ligands)
            res_id = (chain.id, residue.id[1])
            b_list = [atom.bfactor for atom in residue if atom.element != 'H']
            if b_list:  # Only if non-empty
                res_b_factors.setdefault(res_id, []).append(np.mean(b_list))

# Calculate per-residue average B-factor across models
avg_b_factors = {res: np.mean(vals) for res, vals in res_b_factors.items()}

res_indices = [res[1] for res in avg_b_factors.keys()]
b_values = [avg_b_factors[res] for res in avg_b_factors.keys()]

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(res_indices, b_values, label='Average B-factor')
plt.xlabel("Residue Number")
plt.ylabel("B-factor (Å²)")
plt.title("Per-residue B-factor from Ensemble Refinement")
plt.grid(True)
plt.tight_layout()
plt.savefig("B-factor_filtered.jpg", dpi=300)
plt.show()

