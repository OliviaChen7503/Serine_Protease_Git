#!/bin/bash
#SBATCH --nodes=1
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --time=1-00:00:00
#SBATCH --output=quick_submit_1QR3_refine._stdout
#SBATCH --job-name=quick_submit_1QR3_refine

#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true

#________________________________________________CONFIGURATION________________________________________________#
PDB="1QR3"  # Change this for different structures
cd /dors/wankowicz_lab/serine_protease/Elastase/${PDB} || exit 1

phenix.refine 1QR3.mtz 1QR3.updated.pdb DBU.cif refinement.main.number_of_macro_cycles=8 refinement.main.ordered_solvent=True refinement.ordered_solvent.mode=every_macro_cycle refinement.target_weights.optimize_xyz_weight=true refinement.target_weights.optimize_adp_weight=true xray_data.r_free_flags.generate=True refinement.input.xray_data.r_free_flags.label=R-free-flags miller_array.labels.name=FOBS,SIGFOBS
