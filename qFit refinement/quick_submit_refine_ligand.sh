


phenix.refine 2P8O.updated.pdb 2P8O.mtz BVA.cif \
  refinement.input.xray_data.labels="IOBS,SIGIOBS" \
  xray_data.r_free_flags.label="R-free-flags" \
  refinement.main.number_of_macro_cycles=8 \
  refinement.main.ordered_solvent=True \
  refinement.ordered_solvent.mode=every_macro_cycle \
  refinement.target_weights.optimize_xyz_weight=true \
  refinement.target_weights.optimize_adp_weight=true \
  --overwrite#
