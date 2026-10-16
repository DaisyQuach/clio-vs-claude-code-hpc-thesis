// EX16 Stage 1: full cantilever, minimum compliance, OC, Helmholtz filter
// max_iterations 20 from uniform density 0.15; restart file written

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
  boundary_condition_ids 1
  material_interpolation_id 1
end residual

begin material_interpolation 1
  name residual_penalty_model
  type single_phase
  model simp
  penalty_exponent 3.0
  minimum_value 1e-3
end material_interpolation

begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0 0 0
end boundary_condition

begin material 1
  material_model isotropic_elastic
  youngs_modulus 1.0
  poissons_ratio 0.3
end material

begin block 1
  material_id 1
  name block_1
end block

begin criterion 1
  type mechanical_compliance
  material_penalty_exponent 3.0
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

begin filter 1
  type helmholtz
  radius_absolute 0.15
  boundary_sticking_penalty 1.0
end filter

begin study
  optimization_algorithm oc
  max_iterations 20
  discretization density
  initial_density_value 0.15
  normalize_in_aggregator false
  filter_ids 1
  write_restart_file true
  isosurface_output_frequency 1
end study

begin mesh 1
  name mesh.exo
end mesh
