// E3-SPC-v1 Symmetry-Plane Cantilever: minimum-compliance topology optimization of the half
// cantilever z in [0, 0.5]; cut plane z = 0.5 (sideset ss_sym) is a symmetry plane for the
// structural model (dispz = 0) and for the Helmholtz filter (symmetry_plane_location_names).
// Adapted from candidate example_07 (full-domain Helmholtz cantilever) per the frozen specification.

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

// fixed support: x = 0 face, all three displacements
begin boundary_condition 1
  type fixed_value
  location_type nodeset
  location_name ns_fix
  degree_of_freedom dispx dispy dispz
  value 0 0 0
end boundary_condition

// structural symmetry: normal displacement fixed on the cut plane z = 0.5 (sideset)
begin boundary_condition 2
  type fixed_value
  location_type sideset
  location_name ss_sym
  degree_of_freedom dispz
  value 0
end boundary_condition

// transverse line load: -1.0 in y on every node of ns_load (13 nodes, total -13.0)
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

// Helmholtz (PDE) filter via study-level keywords (manual Table 2.5.12 equivalents);
// ss_sym excluded from the boundary-sticking surface term
begin study
  filter_type helmholtz
  filter_radius_absolute 0.15
  boundary_sticking_penalty 1.0
  symmetry_plane_location_names ss_sym
  max_iterations 50
  update_problem_frequency 1
  optimization_algorithm oc
  discretization density
  initial_density_value 0.15
  normalize_in_aggregator false
end study

begin mesh
  name mesh.exo
end mesh
