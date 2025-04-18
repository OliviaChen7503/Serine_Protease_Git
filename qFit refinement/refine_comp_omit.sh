#!/bin/bash
#SBATCH --nodes=1
#SBATCH --array=1-48%100
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --time=0-120:15:00     
#SBATCH --output=Chymotrypsin_refine._stdout
#SBATCH --job-name=Chymotrypsin_refine

#this script will run qfit based on the input PDB names you have.

#________________________________________________INPUTS________________________________________________#
PDB_file=/dors/wankowicz_lab/serine_protease/Chymotrypsin/pdbs.txt
base_dir='/dors/wankowicz_lab/serine_protease/Chymotrypsin'


#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true


#________________________________________________RUN QFIT________________________________________________#
PDB=$(cat $PDB_file | head -n $SLURM_ARRAY_TASK_ID | tail -n 1)
cd ${base_dir}/${PDB}


#RUN REFINEMENT
 cd ${base_dir}/${PDB}
 echo ${PDB}
 phenix.cif_as_mtz ${PDB}-sf.cif --merge
 rm ${PDB}-sf.cif
 mv ${PDB}-sf.mtz ${PDB}.mtz
 phenix.cif_as_pdb ${PDB}.pdb
 phenix.ready_set ${PDB}.pdb


#__________________________________DETERMINE FOBS v IOBS v FP__________________________________
mtzmetadata=`phenix.mtz.dump "${PDB}.mtz"`
# List of Fo types we will check for
obstypes=("FP" "FOBS" "F-obs" "I" "IOBS" "I-obs" "F(+)" "I(+)")

# Get amplitude fields
ampfields=`grep -E "amplitude|intensity|F\(\+\)|I\(\+\)" <<< "${mtzmetadata}"`
ampfields=`echo "${ampfields}" | awk '{$1=$1};1' | cut -d " " -f 1`

# Clear xray_data_labels variable
xray_data_labels=""

# Is amplitude an Fo?
for field in ${ampfields}; do
  # Check field in obstypes
  if [[ " ${obstypes[*]} " =~ " ${field} " ]]; then
    # Check SIGFo is in the mtz too!
    if grep -F -q -w "SIG$field" <<< "${mtzmetadata}"; then
      xray_data_labels="${field},SIG${field}";
      break
    fi
  fi
done



rm ${PDB}.updated.cif

#____________________________RUN REFINEMENT____________________
if [ ! -f "${PDB}.updated_refine_001.pdb" ]; then
 if [ -f "${PDB}.ligands.cif" ]; then
    phenix.refine ${PDB}.mtz ${PDB}.updated.pdb *.cif refinement.main.number_of_macro_cycles=8 refinement.main.ordered_solvent=True refinement.ordered_solvent.mode=every_macro_cycle refinement.target_weights.optimize_xyz_weight=true refinement.target_weights.optimize_adp_weight=true xray_data.r_free_flags.generate=True refinement.input.xray_data.r_free_flags.label=R-free-flags miller_array.labels.name=${xray_data_labels}
 else
  phenix.refine ${PDB}.mtz ${PDB}.updated.pdb refinement.main.number_of_macro_cycles=8 refinement.main.ordered_solvent=True refinement.ordered_solvent.mode=every_macro_cycle refinement.target_weights.optimize_xyz_weight=true refinement.target_weights.optimize_adp_weight=true xray_data.r_free_flags.generate=True refinement.input.xray_data.r_free_flags.label=R-free-flags miller_array.labels.name=${xray_data_labels}
fi
fi

if [ ! -f "composite_omit_map.mtz" ]; then
  #________________________________RUN COMPOSITE OMIT MAP____________________________
  phenix.composite_omit_map ${PDB}.mtz ${PDB}.updated_refine_001.pdb omit-type=refine nproc=1 r_free_flags.generate=True


  #________________________________RUN QFIT____________________________
  qfit_protein composite_omit_map.mtz -l 2FOFCWT,PH2FOFCWT ${PDB}.updated_refine_001.pdb 
  qfit_final_refine_xray.sh ${PDB}.mtz
fi
