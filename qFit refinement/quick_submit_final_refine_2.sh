#!/bin/bash
#SBATCH --job-name=qfit_final_refine_2XDW
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=1-00:00:00
#SBATCH --output=qfit_final_refine_2XDW_%j.out

#________________________________________________SET PATHS________________________________________________#
source /dors/wankowicz_lab/shared/conda/etc/profile.d/conda.sh
conda activate qfit
source /dors/wankowicz_lab/phenix-installer-dev-5366-intel-linux-2.6-x86_64-centos6/phenix-dev-5366/phenix_env.sh
export PHENIX_OVERWRITE_ALL=true

#________________________________________________CONFIGURATION________________________________________________#
PDB="2XDW"  # Change this for different structures
cd /dors/wankowicz_lab/serine_protease/Prolyl_endopeptidase/${PDB} || exit 1

#phenix.composite_omit_map \
   #1QR3.mtz \
   #1QR3.updated_refine_001.pdb \
   #omit-type=refine \
   #nproc=1 \

#qfit_protein composite_omit_map.mtz -l 2FOFCWT,PH2FOFCWT ${PDB}.updated_refine_001.pdb
#qfit_final_refine_xray.sh ${PDB}.mtz

phenix.refine "2XDW_002.pdb" \
            "2XDW_002.mtz" \
            "refine.strategy=*individual_sites *individual_adp *occupancies" \
            "output.prefix=2XDW" \
            "output.serial=5" \
            "refinement.main.number_of_macro_cycles=5" \
            "refinement.main.nqh_flips=False" \
            "refinement.refine.adp.individual.anisotropic=not (water or element H)" \
            "refinement.hydrogens.refine=riding" \
            "refinement.main.ordered_solvent=True" \
            "refinement.target_weights.optimize_xyz_weight=True" \
            "refinement.target_weights.optimize_adp_weight=True" \
            "refinement.input.monomers.file_name='multiconformer_model2.pdb.f_modified.ligands.cif'" \
            qFit_occupancy.params \
            --overwrite

