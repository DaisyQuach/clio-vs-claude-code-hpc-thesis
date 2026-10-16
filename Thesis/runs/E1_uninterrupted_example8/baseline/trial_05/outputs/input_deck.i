// Frozen workflow EX8 (FROZEN-EX8-v1): half cantilever, Helmholtz symmetry-plane filter
// Trial E1-example8-baseline-05. Every value below is locked by scientific_problem_specification.md.

// ---- services: engine (first) and analyze, one processor each ----
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

// ---- scenario / residual ----
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
  boundary_condition_ids 1 2
  material_interpolation_id 1
end residual

// ---- load: concentrated nodal load, direction y, -1.0 per node on ns_load ----
begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

// ---- boundary conditions ----
// fixed support on x = 0 face
begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0.0 0.0 0.0
end boundary_condition

// structural symmetry: u_z = 0 on the cut plane z = 0.5 (sideset ss_sym)
begin boundary_condition 2
  type fixed_value
  location_type sideset
  location_name ss_sym
  degree_of_freedom dispz
  value 0.0
end boundary_condition

// ---- material: isotropic linear elastic, E = 1.0, nu = 0.3 ----
begin material 1
  material_model isotropic_elastic
  youngs_modulus 1.0
  poissons_ratio 0.3
end material

begin block 1
  material_id 1
  name block_1
end block

// ---- SIMP material interpolation: single phase, exponent 3.0, minimum 1e-3 ----
begin material_interpolation 1
  type single_phase
  model simp
  penalty_exponent 3.0
  minimum_value 1e-3
end material_interpolation

// ---- criteria ----
begin criterion 1
  type mechanical_compliance
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

// ---- objective: weighted sum, single compliance criterion, weight 1, analyze service ----
begin objective 1
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

// ---- constraint: volume <= 15 % of design-domain volume, engine service ----
begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
end constraint

// ---- output: nodal displacements from analyze ----
begin output 1
  service_id 2
  data dispx dispy dispz
end output

// ---- study: density topology optimization, OC, 50 iterations ----
begin study
  method topology
  optimization_algorithm oc
  max_iterations 50
  discretization density
  initialize_method uniform
  initial_density_value 0.15
  normalize_in_aggregator false
  // Helmholtz filter (legacy study-level form) with symmetry-plane sideset
  filter_type helmholtz
  filter_radius_absolute 0.15
  boundary_sticking_penalty 1.0
  symmetry_plane_location_names ss_sym
end study

begin mesh 1
  name mesh.exo
end mesh
