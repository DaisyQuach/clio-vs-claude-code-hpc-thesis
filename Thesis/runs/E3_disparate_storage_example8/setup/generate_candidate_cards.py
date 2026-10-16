#!/usr/bin/env python3
"""Generate problem_card.yaml, provenance.yaml and MANIFEST.sha256 for each E3 candidate package from setup/source_inventory.csv."""
import csv, hashlib, os, datetime

E3 = "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8"
CA = E3 + "/chpc_candidate_archive"
NOW = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

OMITTED = [
    "completed final Exodus outputs (engine_output.exo, analyze outputs, per-iteration output directories)",
    "input/meshed Exodus files (regenerate from the journal where a journal is included)",
    "completed topology renderings and optimized-geometry figures",
    "final accepted result summaries and run READMEs",
    "numerical objective/compliance/constraint histories (optimizer diagnostics, criterion CSVs)",
    "solver, Cubit and Slurm logs",
    "generated runtime configuration (XMLGenerator output) of completed runs",
    "researcher validation material and scoring records",
]

PKG = {
 "example_01": dict(
   example=1, title="Topology optimization of a bolted bracket (static compliance, kernel filter)",
   classification="general example",
   role=("Introductory 3-D minimum-compliance topology optimization of a filleted L-bracket with four bolt holes and a "
         "mounting hole: tetrahedral mesh, two element blocks (design block_1, fixed non-design block_2 around the bolts), "
         "fixed nodesets ns_1/ns_2, traction loads on sidesets ss_1/ss_2, steel properties, relative volume constraint 0.3, "
         "kernel filter (radius_scale 2), Optimality Criteria, 100 iterations. Illustrates the general input-deck block "
         "structure (services, criteria, scenario, residual, objective, constraint, output, BCs, loads, blocks, material, "
         "filter, study, mesh)."),
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 1 (manual-shipped input deck and journal)"),
 "example_02": dict(
   example=2, title="Prune-and-refine continuation of the bracket problem",
   classification="distinct workflow",
   role=("Continuation workflow on the Example 1 bracket that adds a prune service (4 processors) and study method "
         "prune_and_topology: the mesh is pruned and refined (number_of_refines 1, number_buffer_layers 2) around an "
         "initial-guess design read from engine_output.exo, with an absolute volume target. It is a distinct multi-service "
         "workflow; it depends on the Example 1 mesh (topology_mech_ex1.exo) and on a completed Example 1 engine output, "
         "neither of which is included here. No journal is shipped for this example (it reuses the Example 1 mesh)."),
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 2 (manual-shipped input deck)"),
 "example_07": dict(
   example=7, title="Full 3-D cantilever with a Helmholtz (PDE) filter and boundary-sticking penalty",
   classification="distinct workflow",
   role=("Minimum-compliance optimization of a full 2 x 1 x 1 cantilever (structured HEX8, 48 x 24 x 24 per the journal), "
         "fixed on x = 0, transverse concentrated line load (direction y, -1 per node) on the edge x = 2, y = 0; "
         "E = 1.0, nu = 0.3; SIMP minimum value 1e-3; weighted-sum compliance objective; relative volume constraint 0.15 "
         "evaluated by the engine service; Helmholtz filter radius_absolute 0.15 with boundary_sticking_penalty 1.0; "
         "OC, 50 iterations, update_problem with frequency 1. A legitimate full-domain workflow that demonstrates the "
         "Helmholtz filter's boundary treatment; it models the whole domain and declares no symmetry plane."),
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 7 (manual-shipped input deck and journal)"),
 "example_16_restart": dict(
   example=16, title="Two-stage restart workflow on the full Helmholtz cantilever",
   classification="restart-specific workflow",
   role=("Restart workflow on the full 2 x 1 x 1 cantilever: stage 1 runs 20 OC iterations with write_restart_file true; "
         "the restart deck runs 40 further iterations starting from the saved design (initial_guess_file_name "
         "initialguess.exo, initial_guess_field_name control, restart_iteration 20). Same physics and filter settings as "
         "the full Helmholtz cantilever; its specific purpose is demonstrating checkpoint/restart of an optimization. "
         "The restart stage needs a stage-1 output (not included)."),
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 16 (manual-shipped stage-1 deck, restart deck and journal)"),
}

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

rows = list(csv.DictReader(open(E3 + "/setup/source_inventory.csv")))
for pkg, m in PKG.items():
    root = f"{CA}/{pkg}"
    files = [r for r in rows if r["e3_destination"].startswith(root + "/")]
    card = [f"# Problem card — E3 candidate package {pkg} (generated {NOW} from setup/source_inventory.csv)",
            f"package_id: {pkg}",
            f"source_example_number: {m['example']}",
            f"title: {q(m['title'])}",
            f"classification: {q(m['classification'])}",
            f"scientific_role: {q(m['role'])}",
            f"shipped_from: {q(m['shipped_from'])}",
            "authenticity: \"files are byte-identical copies of the original sources listed below (SHA-256 verified at copy time)\"",
            "contains_completed_results: false",
            "original_source_locations:"]
    for r in files:
        card.append(f"  - {q(r['original_canonical_path'])}")
    card.append("included_files:")
    for r in files:
        rel = os.path.relpath(r["e3_destination"], root)
        card += [f"  - path: {rel}", f"    role: {q(r['intended_e3_role'])}", f"    file_type: {q(r['file_type'])}",
                 f"    size_bytes: {r['size_bytes']}", f"    sha256: {r['sha256']}"]
    card.append("omitted_result_categories:")
    card += [f"  - {q(o)}" for o in OMITTED]
    card.append("hashes:")
    for r in files:
        card.append(f"  {os.path.relpath(r['e3_destination'], root)}: {r['sha256']}")
    open(root + "/problem_card.yaml", "w").write("\n".join(card) + "\n")

    prov = [f"# Provenance — E3 candidate package {pkg}",
            f"package_id: {pkg}", f"source_example_number: {m['example']}", f"curated_utc: {NOW}",
            "curation_method: \"read-only copy (Python shutil.copy2) of each selected original; SHA-256 of original and copy compared; originals never modified\"",
            "curation_record: /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/source_inventory.csv",
            "files:"]
    for r in files:
        prov += [f"  - destination: {os.path.relpath(r['e3_destination'], root)}",
                 f"    original: {q(r['original_canonical_path'])}",
                 f"    identical_copy_also_at: {q(r['identical_copy_also_at'])}" if r["identical_copy_also_at"] else "    identical_copy_also_at: null",
                 f"    sha256: {r['sha256']}", f"    size_bytes: {r['size_bytes']}"]
    open(root + "/provenance.yaml", "w").write("\n".join(prov) + "\n")
print("cards written")
