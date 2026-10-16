# Score: E2-example16-clio-02

**Decision: accepted** (spec ACCEPT-EX16-v1.1, policy `manual_semantics_iteration_20`, scored 2026-10-13T08:30:27Z)

## Reasons
- [accepted] all predeclared checks passed within accept tolerances against the accepted reference

## Measured values
```json
{
  "packet_verification": "verified",
  "mesh": {
    "path": "outputs/mesh.exo",
    "report": {
      "num_nodes": 30625,
      "num_elem": 27648,
      "block_names": [
        "block_1"
      ],
      "element_type": "HEX8",
      "bbox": [
        0.0,
        0.0,
        0.0,
        2.0,
        1.0,
        1.0
      ],
      "nodesets": {
        "ns_fix": 625,
        "ns_load": 25
      },
      "sidesets": {}
    },
    "checks": {
      "num_elem": true,
      "num_nodes": true,
      "block_1": true,
      "HEX8": true,
      "bbox": true,
      "ns_fix": true,
      "ns_load": true
    }
  },
  "generated_config_stage1": {
    "all_checks_pass": true,
    "fails": [],
    "summary": "33/33 checks pass; all_checks_pass=True"
  },
  "stage2_restart_config": {
    "Iteration": 21,
    "file": "restart_input.exo",
    "field": "control"
  },
  "generated_config_stage2": {
    "all_checks_pass": true,
    "fails": [],
    "summary": "35/35 checks pass; all_checks_pass=True"
  },
  "stage1": {
    "last_iteration": 20,
    "count": 21,
    "stop": true,
    "final_compliance": 236004.0,
    "history_vs_reference": {
      "comparable": true,
      "iterations_compared": 21,
      "max_rel_diff_compliance": 0.0,
      "final_rel_diff_compliance": 0.0,
      "trial_final_compliance": 236004.0,
      "reference_final_compliance": 236004.0,
      "trial_final_H1": 3.964884e-13
    }
  },
  "checkpoint": {
    "path": "outputs/stage1/engine_output.exo",
    "steps": 21,
    "fields": [
      "control",
      "topology"
    ]
  },
  "continuation": {
    "stage2_first_compliance": 236004.0,
    "stage1_compliance_at_matched_iteration": 236004.0,
    "matched_stage1_iteration": 20,
    "match_max_abs_diff": 0.0,
    "compliance_abs_diff_at_match": 0.0,
    "stage2_last_local_iteration": 40,
    "stage2_count": 41,
    "stop": true,
    "stage2_final_compliance": 213558.4,
    "overall_final_iteration_equivalent": 60
  },
  "matched_variant": "manual_semantics_iteration_20",
  "stage2_history_vs_reference": {
    "comparable": true,
    "iterations_compared": 41,
    "max_rel_diff_compliance": 0.0,
    "final_rel_diff_compliance": 0.0,
    "trial_final_compliance": 213558.4,
    "reference_final_compliance": 213558.4,
    "trial_final_H1": -7.552292e-14
  },
  "stage2_final_topology_vs_reference": {
    "comparable": true,
    "max_abs_diff": 0.0,
    "mean_abs_diff": 0.0,
    "node_order_identical": false
  },
  "reference_policy": "manual_semantics_iteration_20",
  "figure": "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/evaluation_figures/E2-example16-clio-02_final_iteration60_vs_manual_semantics_iteration_20.png"
}
```
