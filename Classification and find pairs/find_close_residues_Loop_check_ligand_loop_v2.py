"""
Usage:
This script identifies residues within a specified distance from a target residue in PDB files.
It processes multiple PDB files in a folder based on a chain mapping provided in a CSV file and
outputs results to separate CSV files for ligand and non-ligand cases.

This is Version 2.

Requirements:
- PyMOL must be installed and sourced using: `source /path/to/sbgrid.shrc`.
- Python libraries `pandas` and `csv` must be installed.

Command to run:
python <script_name>.py <pdb_folder> <chain_mapping_csv> <residue_number> <residue_name> <target_atom> <distance> <no_lig_output> <with_lig_output>

Example command:
python find_close_residues.py /path/to/pdb_files /path/to/chain_mapping.csv 195 SER CA 4.0 no_lig_output.csv with_lig_output.csv

python find_close_residues_Loop_check_ligand_loop_v2.py /Users/rosie/Documents/wankowicz_lab/Chymotrypsin/pdb_files /Users/rosie/Documents/wankowicz_lab/Chymotrypsin/chain_mapping_Ligand.csv 195 SER OG 4.0 no_lig_results_v2.csv with_lig_results_v2.csv

Arguments:
- pdb_folder: Path to the folder containing PDB files.
- chain_mapping_csv: Path to the CSV file containing PDB ID, chain mapping, and ligand information.
- residue_number: Residue number of the target residue.
- residue_name: Residue name of the target residue.
- target_atom: Name of the target atom in the residue (e.g., CA for alpha carbon).
- distance: Distance threshold in angstroms to identify residues near the target.
- no_lig_output: Path to the output CSV file for results without ligand.
- with_lig_output: Path to the output CSV file for results with ligand.

Output:
- Two CSV files:
  1. no_lig_output.csv: Contains residues within the specified distance when no ligand is present.
  2. with_lig_output.csv: Contains distances between the target residue and the ligand.
"""



import argparse
import csv
import os
from pymol import cmd
import pandas as pd

def get_min_distance(sel1, sel2):
    # Calculate the minimum distance between two selections
    coords1 = cmd.get_coords(sel1)
    coords2 = cmd.get_coords(sel2)
    min_distance = None
    closest_atom = None
    for c1 in coords1:
        for c2 in coords2:
            d = ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5
            if min_distance is None or d < min_distance:
                min_distance = d
                closest_atom = c2
    return min_distance, closest_atom

def get_nearest_valid_oxygen(carbon_selection, pdb_id):
    # Find the nearest valid oxygen atom to the given carbon atom
    model = cmd.get_model(f"model {pdb_id} and name O")
    carbon_coords = cmd.get_coords(carbon_selection)
    nearest_oxygen = None
    min_distance = None

    for atom in model.atom:
        coords = (atom.coord[0], atom.coord[1], atom.coord[2])
        d = ((carbon_coords[0][0]-coords[0])**2 +
             (carbon_coords[0][1]-coords[1])**2 +
             (carbon_coords[0][2]-coords[2])**2) ** 0.5

        if (min_distance is None or d < min_distance) and d <= 2.2:
            min_distance = d
            nearest_oxygen = {
                "resi": atom.resi,
                "chain": atom.chain,
                "name": atom.name,
                "distance": d,
                "coords": coords
            }

    return nearest_oxygen

def find_closest_residue(pdb_file, residue_number, residue_name, target_atom, chain, distance):
    # Clear all previous selections to avoid conflicts
    cmd.delete('all')

    # Load the PDB file
    cmd.load(pdb_file)
    pdb_id = os.path.basename(pdb_file).rsplit('.', 1)[0]

    # Define the selection for the target residue with the specific atom
    target_selection = f"model {pdb_id} and chain {chain} and resi {residue_number} and resn {residue_name} and name {target_atom}"
    cmd.select('target_residue', target_selection)

    # Ensure target atom exists
    if cmd.count_atoms('target_residue') == 0:
        print(f"Warning: Target atom {target_atom} not found in residue {residue_number} ({residue_name}) of chain {chain}. Skipping.")
        return []

    print(f"Target selection: {target_selection}")

    residues = []
    model = cmd.get_model(f"model {pdb_id} and not chain {chain}")

    # Collect residues with C in the name
    for atom in model.atom:
        resi = atom.resi
        res_chain = atom.chain
        res_name = atom.name

        # Skip if the atom does not meet the carbon condition
        if 'C' not in res_name:
            continue

        # Calculate the distance to the target residue
        residue_selection = f"model {pdb_id} and chain {res_chain} and resi {resi} and name {res_name}"
        min_distance, closest_atom_coords = get_min_distance('target_residue', residue_selection)

        if min_distance <= distance:
            residues.append((resi, res_chain, res_name, min_distance, closest_atom_coords))

    # Sort residues by distance and take the closest one
    if residues:
        closest_residue = sorted(residues, key=lambda x: x[3])[0]
        print(f"Closest residue to target atom {target_atom} in {pdb_id}: {closest_residue}")

        # Find the nearest valid oxygen atom
        carbon_selection = f"model {pdb_id} and chain {closest_residue[1]} and resi {closest_residue[0]} and name {closest_residue[2]}"
        cmd.select('current_carbon', carbon_selection)
        nearest_oxygen = get_nearest_valid_oxygen('current_carbon', pdb_id)

        if nearest_oxygen:
            print(f"  Closest valid oxygen atom: {nearest_oxygen}")
        else:
            print("  No valid oxygen atom within 2.2 Å")

        return [
            {
                "resi": closest_residue[0],
                "chain": closest_residue[1],
                "name": closest_residue[2],
                "distance": closest_residue[3],
                "nearest_oxygen": nearest_oxygen
            }
        ]
    else:
        print(f"No residues with C within {distance} Å found.")
        return []

def process_pdb_files(pdb_folder, chain_mapping_csv, residue_number, residue_name, target_atom, distance, no_lig_output, with_lig_output):
    # Load the chain mapping CSV file and clean column names
    chain_mapping = pd.read_csv(chain_mapping_csv)
    chain_mapping.columns = chain_mapping.columns.str.strip()

    # Check if the Ligand column exists
    if 'Ligand' not in chain_mapping.columns:
        print("Error: 'Ligand' column not found in chain_mapping.csv. Please check the file format.")
        exit()

    no_lig_data = []
    with_lig_data = []

    # Iterate through all PDB files in the folder
    for pdb_file in os.listdir(pdb_folder):
        if pdb_file.endswith('.pdb'):
            pdb_id = pdb_file.rsplit('.', 1)[0].upper()  # Remove file extension and ensure uppercase
            pdb_path = os.path.join(pdb_folder, pdb_file)

            # Get the chain and ligand information for the current PDB file
            chain_info = chain_mapping[chain_mapping['PDB_ID'] == pdb_id]
            if chain_info.empty:
                print(f"Warning: No matching chain information for PDB ID {pdb_id}. Skipping.")
                continue

            chain = chain_info.iloc[0]['Chain_ID']
            ligand = chain_info.iloc[0]['Ligand']
            print(f"Processing PDB: {pdb_id}, Chain: {chain}, Ligand: {ligand}")

            if ligand == 'no_lig':
                # Process the no-ligand logic with the new requirements
                residues = find_closest_residue(pdb_path, residue_number, residue_name, target_atom, chain, distance)
                for residue in residues:
                    oxygen_info = ("None" if residue['nearest_oxygen'] is None else
                                   f"{residue['nearest_oxygen']['name']} (Residue: {residue['nearest_oxygen']['resi']}, Chain: {residue['nearest_oxygen']['chain']}, Distance: {residue['nearest_oxygen']['distance']:.2f}, Coordinates: {residue['nearest_oxygen']['coords']}")
                    no_lig_data.append([pdb_id, residue['resi'], residue['chain'], residue['name'], residue['distance'], oxygen_info])
            else:
                # Process the ligand-specific logic (unchanged)
                cmd.delete('all')  # Clear selections
                cmd.load(pdb_path)
                ligand_selection = f"model {pdb_id} and resn {ligand}"
                cmd.select('ligand', ligand_selection)

                target_selection = f"model {pdb_id} and chain {chain} and resi {residue_number}"
                cmd.select('target_residue', target_selection)

                # Calculate the minimum distance between ligand and target residue
                distance_value = get_min_distance('target_residue', 'ligand')[0]

                # Find the ligand residue number and chain
                ligand_model = cmd.get_model('ligand')
                if ligand_model.atom:
                    lig_residue = ligand_model.atom[0].resi
                    lig_chain = ligand_model.atom[0].chain
                else:
                    lig_residue = 'N/A'
                    lig_chain = 'N/A'

                with_lig_data.append([pdb_id, lig_residue, lig_chain, distance_value, ligand])

                # Clean up
                cmd.delete('target_residue')
                cmd.delete('ligand')

    # Write sorted data to CSV files
    no_lig_df = pd.DataFrame(no_lig_data, columns=['PDB_ID', 'residue_number', 'chain', 'item_name', 'distance', 'nearest_oxygen'])
    with_lig_df = pd.DataFrame(with_lig_data, columns=['PDB_ID', 'lig_Residue', 'chain', 'distance', 'ligand'])

    no_lig_df.sort_values(by='PDB_ID').to_csv(no_lig_output, index=False)
    with_lig_df.sort_values(by='PDB_ID').to_csv(with_lig_output, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find residues within a certain distance of a target residue in PDB files.')
    parser.add_argument('pdb_folder', type=str, help='Path to the folder containing PDB files')
    parser.add_argument('chain_mapping_csv', type=str, help='Path to the CSV file containing PDB ID and chain mapping')
    parser.add_argument('residue_number', type=str, help='Residue number of the target residue')
    parser.add_argument('residue_name', type=str, help='Residue name of the target residue')
    parser.add_argument('target_atom', type=str, help='Name of the target atom in the residue')
    parser.add_argument('distance', type=float, help='Distance threshold in angstroms')
    parser.add_argument('no_lig_output', type=str, help='Path to the output CSV file for no ligand results')
    parser.add_argument('with_lig_output', type=str, help='Path to the output CSV file for ligand results')

    # Parse command-line arguments
    args = parser.parse_args()

    # Process all PDB files and write results to CSV files
    process_pdb_files(args.pdb_folder, args.chain_mapping_csv, args.residue_number, args.residue_name, args.target_atom, args.distance, args.no_lig_output, args.with_lig_output)