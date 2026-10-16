## E3-SPC-v1 Symmetry-Plane Cantilever: minimum-compliance topology optimization of the half domain
## x in [0,2], y in [0,1], z in [0,0.5] of the 2 x 1 x 1 cantilever; cut plane z = 0.5 (sideset ss_sym).
## Adapted from candidate Example 7 (full domain, no symmetry plane): added the symmetry displacement
## condition on ss_sym and declared ss_sym as a symmetry plane of the Helmholtz filter
## (symmetry_plane_location_names in the study block: the filter-block placement was not translated by XMLGenerator).

begin service 1
  code engine
  number_processors 1
  update_problem true
end service

begin service 2
  code analyze
  number_processors 1
end service

begin criterion 1
  type mechanical_compliance
  minimum_ersatz_material_value 1e-3
end criterion

begin criterion 2
  type volume
end criterion

begin scenario 1
  type mechanical
  service_id 2
  dimensions 3
  residual_ids 1
end scenario

begin residual 1
  type mechanical
  load_ids 1
  boundary_condition_ids 1 2
  material_interpolation_id 1
end residual

begin material_interpolation 1
  type single_phase
  model simp
  minimum_value 1e-3
end material_interpolation

begin objective
  type weighted_sum
  criterion_ids 1
  service_ids 2
  scenario_ids 1
  weights 1
end objective

begin output 1
  service_id 2
  output_data true
  data dispx dispy dispz
end output

begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0 0 0
end boundary_condition

begin boundary_condition 2
  type fixed_value
  location_type sideset
  location_name ss_sym
  degree_of_freedom dispz
  value 0
end boundary_condition

begin load 1
  type concentrated_load
  location_type nodeset
  location_name ns_load
  direction y
  value -1.0
end load

begin constraint 1
  criterion_id 2
  relative_target 0.15
  type less_than
  service_id 1
end constraint

begin block 1
  name block_1
  material_id 1
end block

begin material 1
  material_model isotropic_elastic
  poissons_ratio 0.3
  youngs_modulus 1.0
end material

begin filter 1
  type helmholtz
  radius_absolute 0.15
  boundary_sticking_penalty 1.0
end filter

begin study
  filter_ids 1
  max_iterations 50
  update_problem_frequency 1
  optimization_algorithm oc
  discretization density
  initial_density_value 0.15
  normalize_in_aggregator false
  symmetry_plane_location_names ss_sym
end study

begin mesh
  name mesh.exo
end mesh
