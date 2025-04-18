import os
import csv
from Bio.PDB import PDBParser

def find_chain_info(pdb_file, residue_number, residue_name):
    """
    Finds the chain information for a specific residue in a PDB file.
    
    Parameters:
    pdb_file (str): Path to the PDB file.
    residue_number (int): Residue number of interest.
    residue_name (str): Residue name (e.g., SER).
    
    Returns:
    str: Chain ID of the specified residue, or "Not Found" if not found.
    """
    parser = PDBParser(QUIET=True)  # Initialize the PDB parser
    structure = parser.get_structure("pdb_structure", pdb_file)  # Parse the PDB file
    
    for model in structure:  # Loop through models in the PDB file
        for chain in model:  # Loop through chains in the model
            for residue in chain:  # Loop through residues in the chain
                # Check if the residue matches the specified name and number
                if residue.get_resname() == residue_name and residue.id[1] == residue_number:
                    return chain.id  # Return the chain ID
    
    return "Not Found"

def process_pdb_folder(folder_path, residue_number, residue_name, output_csv):
    """
    Processes all PDB files in a folder and writes chain information for a specific residue to a CSV file.
    
    Parameters:
    folder_path (str): Path to the folder containing PDB files.
    residue_number (int): Residue number to search for.
    residue_name (str): Residue name (e.g., SER).
    output_csv (str): Path to the output CSV file.
    """
    # Get a list of all PDB files in the folder
    pdb_files = [f for f in os.listdir(folder_path) if f.endswith(".pdb")]

    if not pdb_files:
        print("No PDB files found in the specified folder.")
        return

    with open(output_csv, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["PDB Name", "Chain ID"])  # Write header row

        for pdb_file in pdb_files:
            pdb_path = os.path.join(folder_path, pdb_file)
            chain_id = find_chain_info(pdb_path, residue_number, residue_name)
            csv_writer.writerow([pdb_file, chain_id])  # Write PDB name and chain ID

    print(f"Output written to {output_csv}")

# Example usage
if __name__ == "__main__":
    import argparse

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Find the chain information of a residue in multiple PDB files and save to CSV.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing PDB files.")
    parser.add_argument("residue_number", type=int, help="Residue number to search for.")
    parser.add_argument("residue_name", type=str, help="Residue name (e.g., SER).")
    parser.add_argument("output_csv", type=str, help="Path to the output CSV file.")

    args = parser.parse_args()

    # Process the folder and write to CSV
    process_pdb_folder(args.folder_path, args.residue_number, args.residue_name, args.output_csv)
