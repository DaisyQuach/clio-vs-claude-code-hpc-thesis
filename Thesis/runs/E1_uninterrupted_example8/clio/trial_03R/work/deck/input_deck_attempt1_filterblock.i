// FROZEN-EX8-v1: half cantilever, minimum compliance, Helmholtz symmetry-plane filter
// services: engine first (one processor), analyze second (one processor)
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

// concentrated nodal load, direction y, -1.0 per node on ns_load (13 nodes)
begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

// fixed support on x = 0 face
begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0.0 0.0 0.0
end boundary_condition

// structural symmetry on the cut plane z = 0.5 (sideset ss_sym): u_z = 0
begin boundary_condition 2
  type fixed_value
  location_type sideset
  location_name ss_sym
  degree_of_freedom dispz
  value 0.0
end boundary_condition

begin material 1
  material_model isotropic_elastic
  youngs_modulus 1.0
  poissons_ratio 0.3
end material

// SIMP single phase, exponent 3.0 (runtime default), minimum value 1e-3
begin material_interpolation 1
  name simp_model
  type single_phase
  model simp
  minimum_value 1e-3
  penalty_exponent 3.0
end material_interpolation

begin block 1
  material_id 1
  name block_1
end block

begin criterion 1
  type mechanical_compliance
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

begin objective
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

// volume <= 15 % of design-domain volume, evaluated by the engine service
begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
  scenario_id 1
end constraint

begin output 1
  service_id 2
  data dispx dispy dispz
end output

// Helmholtz (PDE) filter, absolute radius 0.15, sticking penalty 1.0, symmetry plane ss_sym
begin filter 1
  type helmholtz
  radius_absolute 0.15
  boundary_sticking_penalty 1.0
  symmetry_plane_location_names ss_sym
end filter

begin study
  optimization_algorithm oc
  max_iterations 50
  discretization density
  initial_density_value 0.15
  normalize_in_aggregator false
  filter_ids 1
end study

begin mesh
  name mesh.exo
end mesh
