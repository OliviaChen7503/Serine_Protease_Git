#!/bin/bash
#SBATCH --nodes=1
#SBATCH --array=1-9%10       # Replace N with total PDBs, MAX with max concurrent jobs
#SBATCH --mem=16G
#SBATCH --cpus-per-task=3
#SBATCH --time=5-00:00:00
#SBATCH --output=quick_submit_%A_%a_stdout
#SBATCH --job-name=quick_submit_Thrombin_refine

#________________________________________________COMMENTS________________________________________________#
# Submit all jobs:       sbatch quick_submit_refine.sh refine
# Submit single job:     sbatch --array=<TASK_ID> quick_submit_refine.sh omit_map
# Supported operations:  refine / omit_map / qfit

#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true

#________________________________________________INPUTS________________________________________________#
PDB_FILE="/dors/wankowicz_lab/serine_protease/Thrombin/pdbs_1.txt"  # Path to your PDB list
BASE_DIR="/dors/wankowicz_lab/serine_protease/Thrombin"

#________________________________________________CONFIGURATION________________________________________________#
PDB=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $PDB_FILE)  # Get PDB for current array task
cd ${BASE_DIR}/${PDB} || exit 1

#________________________________________________FUNCTIONS________________________________________________#
run_refinement() {
  echo "Starting refinement for ${PDB}..."
  phenix.refine ${PDB}.mtz ${PDB}.updated.pdb \
    xray_data.r_free_flags.generate=True \
    refinement.main.number_of_macro_cycles=8 \
    refinement.main.ordered_solvent=True \
    refinement.target_weights.optimize_xyz_weight=true \
    --overwrite
}

run_omit_map() {
  echo "Generating composite omit map for ${PDB}..."
  phenix.composite_omit_map ${PDB}.mtz ${PDB}.updated_refine_001.pdb \
    omit-type=refine \
    nproc=1
}

run_qfit() {
  echo "Running qFit for ${PDB}..."
  qfit_protein composite_omit_map.mtz -l 2FOFCWT,PH2FOFCWT ${PDB}.updated_refine_001.pdb -p 6
  qfit_final_refine_xray.sh ${PDB}.mtz
}

#________________________________________________MAIN________________________________________________#
case $1 in
  refine)
    run_refinement
    ;;
  omit_map)
    run_omit_map
    ;;
  qfit)
    run_qfit
    ;;
  *)
    echo "Usage: $0 [refine|omit_map|qfit]"
    echo "Example: sbatch --array=1-10 quick_submit_refine.sh refine"
    exit 1
    ;;
esac

echo "Job ${SLURM_ARRAY_TASK_ID} (${PDB}) completed: $(date)"
