#!/bin/bash
#SBATCH --nodes=1
#SBATCH --array=1-10000%150
#SBATCH --mem=12G
#SBATCH --cpus-per-task=1
#SBATCH --time=0-34:15:00     
#SBATCH --output=qfit_refine_30._stdout
#SBATCH --job-name=qfit_30refine

#this script will run qfit based on the input PDB names you have.

#________________________________________________INPUTS________________________________________________#
PDB_file=/dors/wankowicz_lab/all_pdb/30001_40000/pdb_30001_40000.txt
base_dir='/dors/wankowicz_lab/all_pdb/30001_40000/'

#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true


#________________________________________________RUN QFIT________________________________________________#
PDB=$(cat $PDB_file | head -n $SLURM_ARRAY_TASK_ID | tail -n 1)
cd ${base_dir}/${PDB}



if [ ! -f "multiconformer_model2.pdb" ]; then
  #________________________________RUN QFIT____________________________
  qfit_protein composite_omit_map.mtz -l 2FOFCWT,PH2FOFCWT ${PDB}.updated_refine_001.pdb
  #qfit_final_refine_xray.sh ${PDB}.mtz
fi

if [ ! -f "${PDB}_qFit.pdb" ]; then
  #________________________________RUN QFIT____________________________
  #qfit_protein composite_omit_map.mtz -l 2FOFCWT,PH2FOFCWT ${PDB}.updated_refine_001.pdb
  qfit_final_refine_xray.sh ${PDB}.mtz
fi
