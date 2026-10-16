// Frozen workflow EX16 (FROZEN-EX16-v1) - Stage 2 (continuation: 40 further iterations from the iteration-20 design of Stage 1)
// Minimum-compliance topology optimization of a 3D cantilever, volume <= 15 %

// engine service: optimizer; update_problem true with frequency 1 (locked)
begin service 1
  code engine
  number_processors 1
  update_problem true
  update_problem_frequency 1
end service

// analyze service: physics (single rank, no decomposition)
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

// SIMP single phase, exponent 3.0, minimum value 1e-3 (locked)
begin material_interpolation 1
  type single_phase
  model simp
  penalty_exponent 3.0
  minimum_value 1e-3
end material_interpolation

// concentrated nodal load, -1.0 in y on every node of ns_load (25 nodes, total -25.0)
begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

// fixed support on the x = 0 face
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

// compliance criterion with locked ersatz parameters
begin criterion 1
  type mechanical_compliance
  material_penalty_exponent 3.0
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

// weighted-sum objective, single compliance criterion, weight 1, evaluated by analyze (service 2)
begin objective
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

// volume <= 0.15 of design-domain volume, evaluated by the engine (service 1)
begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
  scenario_id 1
end constraint

// Helmholtz filter, absolute radius 0.15, boundary sticking penalty 1.0, no symmetry plane
begin filter 1
  type helmholtz
  radius_absolute 0.15
  boundary_sticking_penalty 1.0
end filter

// analyze output: nodal displacements every iteration
begin output 1
  service_id 2
  data dispx dispy dispz
  output_frequency 1
end output

// Stage 2: OC, 40 further iterations, restart from the Stage-1 checkpoint copy restart_input.exo (field control), restart writing kept enabled
begin study
  method topology
  optimization_algorithm oc
  max_iterations 40
  discretization density
  filter_ids 1
  normalize_in_aggregator false
  write_restart_file true
  // restart source: exact copy of outputs/stage1/engine_output.exo; field control (raw design variable); saved state = 21
  initial_guess_file_name restart_input.exo
  initial_guess_field_name control
  restart_iteration 21
  // engine output file written every iteration (XMLGenerator parameter; sets PlatoMainOutput OutputFrequency 1) so all 21 states are saved
  isosurface_output_frequency 1
  verbose true
end study

begin mesh
  name mesh.exo
end mesh
