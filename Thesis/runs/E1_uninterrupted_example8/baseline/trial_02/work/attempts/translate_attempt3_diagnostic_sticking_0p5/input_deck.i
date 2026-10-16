// Frozen workflow EX8 (FROZEN-EX8-v1): half cantilever with a Helmholtz symmetry-plane filter
// Trial E1-example8-baseline-02. Every value below follows scientific_problem_specification.md.

// ---- Services: engine first (one processor), then analyze (one processor) ----
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

// ---- Scenario / residual ----
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

// ---- Load: concentrated nodal load, direction y, -1.0 per node on ns_load (13 nodes, total -13.0) ----
begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

// ---- Boundary conditions ----
// Fixed support on x = 0 face
begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0.0 0.0 0.0
end boundary_condition

// Structural symmetry on the cut plane z = 0.5 (normal displacement fixed, applied through the sideset)
begin boundary_condition 2
  type fixed_value
  location_type sideset
  location_name ss_sym
  degree_of_freedom dispz
  value 0.0
end boundary_condition

// ---- Material: isotropic linear elastic, E = 1.0, nu = 0.3 ----
begin material 1
  material_model isotropic_elastic
  youngs_modulus 1.0
  poissons_ratio 0.3
end material

// ---- Material interpolation: SIMP, single phase, exponent 3.0, minimum value 1e-3 ----
begin material_interpolation 1
  type single_phase
  model simp
  penalty_exponent 3.0
  minimum_value 1e-3
end material_interpolation

// ---- Single optimizable block ----
begin block 1
  material_id 1
  name block_1
end block

// ---- Criteria ----
begin criterion 1
  type mechanical_compliance
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

// ---- Objective: weighted sum, single compliance criterion, weight 1, evaluated by analyze ----
begin objective 1
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

// ---- Constraint: volume <= 15 % of the design-domain volume, evaluated by the engine ----
begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
end constraint

// ---- Output: nodal displacements from analyze (engine always writes control and topology) ----
begin output 1
  service_id 2
  data dispx dispy dispz
end output

// ---- Study: density-based topology optimization, OC, exactly 50 iterations ----
begin study
  method topology
  optimization_algorithm oc
  max_iterations 50
  discretization density
  initialize_method uniform
  initial_density_value 0.15
  normalize_in_aggregator false
  // Helmholtz filter (legacy study-level form): absolute radius 0.15, boundary-sticking penalty 1.0, symmetry plane ss_sym
  filter_type helmholtz
  filter_radius_absolute 0.15
  boundary_sticking_penalty 0.5
  symmetry_plane_location_names ss_sym
end study

begin mesh
  name mesh.exo
end mesh
