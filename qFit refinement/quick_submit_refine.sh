#!/bin/bash
#SBATCH --nodes=1
#SBATCH --mem=16G
#SBATCH --cpus-per-task=3
#SBATCH --time=2-00:00:00
#SBATCH --output=quick_submit_3M7Q_refine._stdout
#SBATCH --job-name=quick_submit_3M7Q_refine

#________________________________________________COMMENTS________________________________________________#
#sbatch your_script.sh refine       To Run refinement
#sbatch your_script.sh omit_map     To Run omit map
#sbatch your_script.sh qfit         To Run qFit

#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true

#________________________________________________CONFIGURATION________________________________________________#
PDB="3M7Q"  # Change this for different structures
cd /dors/wankowicz_lab/serine_protease/Trypsin/${PDB} || exit 1

#________________________________________________FUNCTIONS________________________________________________#
run_refinement() {
  echo "Starting refinement for ${PDB}..."
  phenix.refine ${PDB}.mtz ${PDB}.updated.pdb \
    xray_data.r_free_flags.generate=True \
    refinement.main.number_of_macro_cycles=8 \
    refinement.main.ordered_solvent=True \
    refinement.target_weights.optimize_xyz_weight=true \
    refinement.target_weights.optimize_adp_weight=true \
    refinement.input.xray_data.r_free_flags.label=R-free-flags\
    miller_array.labels.name=FOBS,SIGFOBS \
    --overwrite
}

run_omit_map() {
  echo "Generating composite omit map for ${PDB}..."
  phenix.composite_omit_map \
    ${PDB}.mtz \
    ${PDB}.updated_refine_001.pdb \
    omit-type=refine \
    nproc=1 \
}

run_qfit() {
  echo "Running qFit for ${PDB}..."
  qfit_protein composite_omit_map.mtz -l 2FOFCWT,PH2FOFCWT ${PDB}.updated_refine_001.pdb
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
    echo "Example: sbatch script_name.sh refine"
    exit 1
    ;;
esac

echo "Job completed: $(date)"
