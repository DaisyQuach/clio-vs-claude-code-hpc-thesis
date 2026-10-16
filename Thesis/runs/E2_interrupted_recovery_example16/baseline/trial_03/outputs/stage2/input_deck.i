// FROZEN-EX16-v1 -- Stage 2 (continuation) of the two-stage (restartable) cantilever compliance-minimization workflow
// Trial E2-example16-baseline-03. Every value below is the locked value from scientific_problem_specification.md.
// Stage 2: resumes from the iteration-20 design saved at the end of Stage 1, read from the 'control' field of
// restart_input.exo (an exact copy of the Stage-1 checkpoint outputs/stage1/engine_output.exo), and runs
// max_iterations 40 further iterations (overall iteration 60). All physics/optimization settings are identical to Stage 1.

// ---- services (engine first; one processor each; single-rank performers) ----
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

// ---- physics ----
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

// concentrated nodal load on every node of ns_load, direction y, -1.0 per node (25 nodes, total -25.0)
begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

// fixed support: all displacement components zero on nodeset ns_fix (face x = 0)
begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0.0 0.0 0.0
end boundary_condition

// isotropic linear elastic, E = 1.0, nu = 0.3
begin material 1
  material_model isotropic_elastic
  youngs_modulus 1.0
  poissons_ratio 0.3
  material_interpolation_id 1
end material

// SIMP, single phase, exponent 3.0, minimum value 1e-3
begin material_interpolation 1
  type single_phase
  model simp
  penalty_exponent 3.0
  minimum_value 1e-3
end material_interpolation

// exactly one element block containing the whole (optimizable) domain
begin block 1
  name block_1
  material_id 1
end block

// ---- optimization ----
begin criterion 1
  type mechanical_compliance
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

begin objective 1
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

// volume <= 15 % of the design-domain volume, evaluated by the engine service
begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
end constraint

// Helmholtz (PDE) filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane
begin filter 1
  type helmholtz
  radius_absolute 0.15
  boundary_sticking_penalty 1.0
end filter

// nodal displacements from analyze; engine writes control/topology fields (output_data default true)
begin output 1
  service_id 2
  data dispx dispy dispz
end output

begin study 1
  method topology
  optimization_algorithm oc
  max_iterations 40
  discretization density
  normalize_in_aggregator false
  filter_ids 1
  // ---- restart (continuation) settings: iteration-20 design from the 'control' field of the checkpoint copy ----
  // restart_iteration is the 1-based Exodus time step of the checkpoint: time step 21 holds the iteration-20 design
  // (attempt 1 with restart_iteration 20 read the iteration-19 design: first compliance 2.388394e+05 = Stage-1 iteration 19; job 16166532 cancelled)
  initial_guess_file_name restart_input.exo
  initial_guess_field_name control
  restart_iteration 21
  // keep writing the engine output (control + topology) at EVERY iteration so Stage 2's saved states are preserved
  write_restart_file true
  isosurface_output_frequency 1
end study

begin mesh 1
  name mesh.exo
end mesh
