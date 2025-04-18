import argparse
import csv
import os
from pymol import cmd

def get_min_distance(sel1, sel2):
    """Calculate minimum distance between two selections."""
    coords1 = cmd.get_coords(sel1)
    coords2 = cmd.get_coords(sel2)
    min_distance = None
    for c1 in coords1:
        for c2 in coords2:
            d = ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5
            if min_distance is None or d < min_distance:
                min_distance = d
    return min_distance

def find_all_distances(pdb_file, target_res_num, target_chain, output_dir):
    """Calculate distances from target residue to ALL other residues."""
    cmd.load(pdb_file)
    pdb_id = os.path.basename(pdb_file).split('.')[0]
    target_sel = f'chain {target_chain} and resi {target_res_num}'
    cmd.select('target', target_sel)

    # Get all residues except the target
    cmd.select('all_residues', 'not target')
    model = cmd.get_model('all_residues')
    residues = set((atom.resi, atom.chain) for atom in model.atom)

    # Write distances to CSV
    output_file = os.path.join(output_dir, f"{pdb_id}_all_distances.csv")
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['resi', 'chain', 'distance'])
        for resi, chain in residues:
            res_sel = f'chain {chain} and resi {resi}'
            distance = get_min_distance('target', res_sel)
            writer.writerow([resi, chain, distance])

    cmd.delete('target')
    cmd.delete('all_residues')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate distances from a target residue to ALL residues.')
    parser.add_argument('pdb_file', help='Path to PDB file')
    parser.add_argument('target_res_num', help='Target residue number')
    parser.add_argument('target_chain', help='Target residue chain')
    parser.add_argument('--output_dir', default='.', help='Output directory')
    args = parser.parse_args()
    
    find_all_distances(args.pdb_file, args.target_res_num, args.target_chain, args.output_dir)
