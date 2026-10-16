// Stage-1 input deck -- frozen workflow EX16 (FROZEN-EX16-v1)
// Minimum-compliance topology optimization of a 3D cantilever, Stage 1 of the two-stage restart workflow.
// Stage 1: fresh start from uniform density 0.15, max_iterations 20, restart-file writing enabled.

// ---------------- services (engine first; single-rank performers, no mesh decomposition) ----------------
begin service 1
  code engine
  number_processors 1
  update_problem true
  update_problem_frequency 1
end service

begin service 2
  code analyze
  number_processors 1
end service

// ---------------- scenario / residual ----------------
begin scenario 1
  type mechanical
  dimensions 3
  service_id 2
  residual_ids 1
  output_id 1
end scenario

begin residual 1
  type mechanical
  load_ids 1
  boundary_condition_ids 1
  material_interpolation_id 1
end residual

// ---------------- load: concentrated nodal load, direction y, -1.0 per node on ns_load (25 nodes) ----------------
begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

// ---------------- fixed support: ns_fix, u_x = u_y = u_z = 0 ----------------
begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0.0 0.0 0.0
end boundary_condition

// ---------------- material: isotropic linear elastic, E = 1.0, nu = 0.3 ----------------
begin material 1
  material_model isotropic_elastic
  youngs_modulus 1.0
  poissons_ratio 0.3
end material

begin block 1
  name block_1
  material_id 1
end block

// ---------------- SIMP material interpolation: single phase, exponent 3.0, minimum value 1e-3 ----------------
begin material_interpolation 1
  type single_phase
  model simp
  penalty_exponent 3.0
  minimum_value 1e-3
end material_interpolation

// ---------------- criteria ----------------
begin criterion 1
  type mechanical_compliance
  material_penalty_exponent 3.0
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

// ---------------- objective: weighted sum, single compliance criterion, weight 1, analyze service ----------------
begin objective 1
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

// ---------------- constraint: volume <= 15 % of design-domain volume, engine service ----------------
begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
end constraint

// ---------------- output: nodal displacements from analyze (engine always writes control and topology) ----------------
begin output 1
  service_id 2
  data dispx dispy dispz
end output

// ---------------- Helmholtz (PDE) filter: absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane ----------------
begin filter 1
  type helmholtz
  radius_absolute 0.15
  boundary_sticking_penalty 1.0
end filter

// ---------------- study: density TO, OC optimizer, Stage-1 iteration cap 20, restart-file writing ----------------
begin study
  method topology
  discretization density
  optimization_algorithm oc
  max_iterations 20
  initialize_method uniform
  initial_density_value 0.15
  normalize_in_aggregator false
  filter_ids 1
  write_restart_file true
  // engine output (control + topology) written at EVERY iteration -> 21 saved states (iterations 0-20)
  isosurface_output_frequency 1
  verbose true
end study

begin mesh 1
  name mesh.exo
end mesh
