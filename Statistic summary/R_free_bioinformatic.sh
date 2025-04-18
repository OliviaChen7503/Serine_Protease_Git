#!/bin/bash
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --array=1-66%10
#SBATCH --output=bioinformatics_stdout

#__________________LOAD PHENIX/QFIT ENVIRONMENTS________________________________________________#
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true

# Activate qFit conda environment
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit

#________________PDB INPUT CONFIGURATION__________________________________
PDB_file=/dors/wankowicz_lab/serine_protease/Elastase/pdbs_5.txt
PDB_dir='/dors/wankowicz_lab/serine_protease/Elastase'
output_dir='/dors/wankowicz_lab/serine_protease/Elastase/output'

cd ${output_dir}

# Get current PDB ID from job array index
PDB=$(cat $PDB_file | head -n $SLURM_ARRAY_TASK_ID | tail -n 1)
echo "Processing PDB: $PDB"

#______________________EXTRACT R-FREE AND SAVE AS CSV_______________________
# Run Python script to parse log file and generate CSV with headers
python /dors/wankowicz_lab/ensemble_bioinformatic_toolkit/multiconformer_tools/single_parse_log.py \
  ${PDB_dir}/${PDB}/${PDB}_qFit.log ${PDB} > ${output_dir}/${PDB}_rvalues.csv

#__________________MERGE ALL CSV FILES AFTER JOB ARRAY COMPLETION___________________
# Only the last task in the array (ID=34) triggers merging
if [ "$SLURM_ARRAY_TASK_ID" -eq 66 ]; then
  # Wait for all tasks to finish writing files
  sleep 30  # Adjust based on expected processing time
  
  # Merge CSVs using awk:
  # - Keep header from the first file
  # - Skip headers from subsequent files
  awk '
    FNR == 1 && !header_printed {  # Print header only once
      print; 
      header_printed = 1;
      next
    } 
    FNR > 1  # Skip headers in other files
  ' ${output_dir}/*_rvalues.csv > ${output_dir}/all_rvalues.csv

  # Optional: Clean temporary CSV files
  rm ${output_dir}/*_rvalues.csv
fi
