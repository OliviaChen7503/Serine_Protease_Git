#!/bin/bash

#-------------------------------Configuration Section-------------------------------#
PDB_PAIR_LIST="pdb_pairs.txt"  # Input file with PDB pairs (one pair per line: "PDB1_path PDB2_path")
OUTPUT_DIR="rmsd_results"       # Output directory for results

#-------------------------------Script Start-------------------------------#
mkdir -p ${OUTPUT_DIR}

# Create result header
echo -e "PDB1\tPDB2\tRMSD" > ${OUTPUT_DIR}/all_results.tsv

echo "Processing PDB pairs from: ${PDB_PAIR_LIST}"
echo "----------------------------------------"

# Process input file line by line
while IFS= read -r line; do
  # Extract PDB paths
  PDB1=$(echo "$line" | awk '{print $1}')
  PDB2=$(echo "$line" | awk '{print $2}')

  # Check input integrity
  if [[ -z "$PDB1" || -z "$PDB2" ]]; then
    echo "[ERROR] Invalid line format: $line" >&2
    continue
  fi

  # Check file existence
  if [[ ! -f "$PDB1" ]]; then
    echo "[ERROR] File not found: $PDB1" >&2
    continue
  fi
  if [[ ! -f "$PDB2" ]]; then
    echo "[ERROR] File not found: $PDB2" >&2
    continue
  fi

  # Extract base PDB names for reporting
  BASE1=$(basename "${PDB1}" .pdb)
  BASE2=$(basename "${PDB2}" .pdb)

  # Perform RMSD calculation
  echo "Processing pair: ${BASE1} ↔ ${BASE2}"
  RMSD=$(python - <<END
from pymol import cmd
cmd.load("$PDB1", "mobile")
cmd.load("$PDB2", "target")
rmsd = cmd.align("mobile & chain A & name CA", 
                 "target & chain A & name CA",
                 cycles=0)[0]
print(f"{rmsd:.3f}")
END
  )

  # Record results (PDB names and RMSD)
  echo -e "${BASE1}\t${BASE2}\t${RMSD}" >> ${OUTPUT_DIR}/all_results.tsv

done < "${PDB_PAIR_LIST}"

echo "----------------------------------------"
echo "All tasks completed! Results saved to: ${OUTPUT_DIR}/all_results.tsv"