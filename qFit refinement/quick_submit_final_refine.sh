#!/bin/bash
#SBATCH --job-name=qfit_final_Elastase_refine
#SBATCH --nodes=1
#SBATCH --array=1-7%10       # Replace N with total PDBs, MAX with max concurrent jobs
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=24:00:00
#SBATCH --output=qfit_final_refine_%A_%a.out  # %A=jobID, %a=arrayIndex

#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true

#________________________________________________INPUTS________________________________________________#
PDB_FILE="/dors/wankowicz_lab/serine_protease/Elastase/pdbs_2.txt"  # Path to your PDB list
BASE_DIR="/dors/wankowicz_lab/serine_protease/Elastase"

#________________________________________________CONFIGURATION________________________________________________#
# Get PDB for current array task
PDB=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$PDB_FILE")
cd "${BASE_DIR}/${PDB}" || exit 1

#________________________________________________RUN QFIT FINAL REFINEMENT________________________________________________#
echo "Starting qfit final refinement for ${PDB} (Task ${SLURM_ARRAY_TASK_ID}) at $(date)"
qfit_final_refine_xray.sh "${PDB}.mtz"
echo "Job ${SLURM_ARRAY_TASK_ID} (${PDB}) completed at $(date)"
