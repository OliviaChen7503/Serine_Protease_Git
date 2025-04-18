#!/usr/bin/env python
import sys
import os
from pymol import cmd

# Define input file with PDB pairs
input_file = "pdb_pairs.txt"

# Output file for results
output_file = "batch_rmsd_results.txt"

# Open the output file to store results
with open(output_file, "w") as out_f:
    out_f.write("Structure 1\tStructure 2\tAlpha Carbon RMSD (Å)\n")

    # Read each PDB pair from the input file
    with open(input_file, "r") as f:
        for line in f:
            structure_1, structure_2 = line.strip().split()

            # Load structures into PyMOL
            cmd.reinitialize()  # Reset PyMOL for each pair
            cmd.load(structure_1, "structure_1")
            cmd.load(structure_2, "structure_2")

            # Select alpha carbon atoms of chain A
            cmd.select("chain_A_1", "structure_1 and chain A and name CA")
            cmd.select("chain_A_2", "structure_2 and chain A and name CA")

            # Check if selections contain atoms
            if cmd.count_atoms("chain_A_1") == 0 or cmd.count_atoms("chain_A_2") == 0:
                print(f"Skipping {structure_1} and {structure_2}: No CA atoms in Chain A")
                continue

            # Compute RMSD
            rmsd = cmd.align("chain_A_1", "chain_A_2")[0]

            # Write results to file
            out_f.write(f"{structure_1}\t{structure_2}\t{rmsd:.3f}\n")

            print(f"Processed: {structure_1} vs {structure_2} | RMSD: {rmsd:.3f} Å")

print(f"Batch processing complete. Results saved in {output_file}.")

