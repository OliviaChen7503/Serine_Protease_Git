from Bio import PDB

def rename_chains(pdb_file, output_file, chain_mapping):
    """
    Rename specific chains in a PDB file.

    Parameters:
    - pdb_file: Input PDB file path.
    - output_file: Output PDB file path.
    - chain_mapping: Dictionary mapping old chain IDs to new chain IDs.
    """
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("structure", pdb_file)

    for model in structure:
        for chain in model:
            if chain.id in chain_mapping:
                chain.id = chain_mapping[chain.id]  # Rename the chain

    io = PDB.PDBIO()
    io.set_structure(structure)
    io.save(output_file)

# Define the chain mappings
chain_map = {
    "E": "A",
    "F": "B",
    "G": "C"
}

# Usage Example
rename_chains("input.pdb", "output.pdb", chain_map)
