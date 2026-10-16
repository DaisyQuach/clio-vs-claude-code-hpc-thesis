#!/usr/bin/env python3
"""E3 remediation (researcher-side only): curate the Example 13 replacement package and regenerate every candidate
package card with LOGICAL source identifiers instead of original absolute paths.

- copies the selected Example 13 originals (read-only on the source side; SHA-256 of original and copy compared)
- rewrites problem_card.yaml / provenance.yaml of every package (no original absolute paths)
- rewrites the archive README.md and MANIFEST.sha256
- writes the complete canonical mapping ONLY to researcher_only/provenance/
Write protection of the archive is lifted only for the duration of the write and restored afterwards (dirs 555, files 444).
"""
import csv, datetime, hashlib, os, shutil, stat, sys

E3 = "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8"
CA = E3 + "/chpc_candidate_archive"
PROV = E3 + "/researcher_only/provenance"
REM = E3 + "/setup/remediation"
D = "/uufs/chpc.utah.edu/common/home/chet/Daisy"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

# ---------------------------------------------------------------- Example 13 (replacement) sources
EX13_DIR = D + "/Morphorm_Full_Examples_Tests/Example13_2D"
DOCS_MECH = D + "/Morphorm/docs/examples/input_decks/topology_optimization/mech"
EX13 = [  # (original, identical copy also at, destination name, file type, role, logical file id)
    (EX13_DIR + "/topology_mech_ex13.i", DOCS_MECH + "/topology_mech_ex13.i", "topology_mech_ex13.i",
     "Morphorm input deck (text)", "candidate input deck (Example 13, as shipped)", "input_deck"),
    (EX13_DIR + "/topology_mech_ex13.jou", DOCS_MECH + "/topology_mech_ex13.jou", "topology_mech_ex13.jou",
     "Coreform Cubit journal (text)", "candidate mesh-generation journal (Example 13, as shipped)", "journal"),
    (D + "/Morphorm/docs/examples/figs/topology_optimization/mech/ex13/topology_2d_model_ex13.png", "",
     "problem_geometry_figure.png", "PNG image", "problem-statement geometry/mesh figure (no result)", "problem_figure"),
]

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
   example=1, logical="MORPHORM-CANDIDATE-EX01",
   title="Topology optimization of a bolted bracket (static compliance, kernel filter)",
   classification="general example",
   role=("Introductory 3-D minimum-compliance topology optimization of a filleted L-bracket with four bolt holes and a "
         "mounting hole: tetrahedral mesh, two element blocks (design block_1, fixed non-design block_2 around the bolts), "
         "fixed nodesets ns_1/ns_2, traction loads on sidesets ss_1/ss_2, steel properties, relative volume constraint 0.3, "
         "kernel filter (radius_scale 2), Optimality Criteria, 100 iterations. Illustrates the general input-deck block "
         "structure (services, criteria, scenario, residual, objective, constraint, output, BCs, loads, blocks, material, "
         "filter, study, mesh)."),
   self_contained="yes: the journal generates the mesh the deck reads; no other example's files or outputs are needed",
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 1 (manual-shipped input deck and journal)",
   files={"topology_mech_ex1.i": "input_deck", "topology_mech_ex1.jou": "journal", "problem_geometry_figure.png": "problem_figure"}),
 "example_07": dict(
   example=7, logical="MORPHORM-CANDIDATE-EX07",
   title="Full 3-D cantilever with a Helmholtz (PDE) filter and boundary-sticking penalty",
   classification="distinct workflow",
   role=("Minimum-compliance optimization of a full 2 x 1 x 1 cantilever (structured HEX8, 48 x 24 x 24 per the journal), "
         "fixed on x = 0, transverse concentrated line load (direction y, -1 per node) on the edge x = 2, y = 0; "
         "E = 1.0, nu = 0.3; SIMP minimum value 1e-3; weighted-sum compliance objective; relative volume constraint 0.15 "
         "evaluated by the engine service; Helmholtz filter radius_absolute 0.15 with boundary_sticking_penalty 1.0; "
         "OC, 50 iterations, update_problem with frequency 1. A legitimate full-domain workflow that demonstrates the "
         "Helmholtz filter's boundary treatment; it models the whole domain and declares no symmetry plane."),
   self_contained="yes: the journal generates the mesh the deck reads; no other example's files or outputs are needed",
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 7 (manual-shipped input deck and journal)",
   files={"topology_mech_ex7.i": "input_deck", "topology_mech_ex7.jou": "journal", "problem_geometry_figure.png": "problem_figure"}),
 "example_13": dict(
   example=13, logical="MORPHORM-CANDIDATE-EX13",
   title="2-D L-bracket (plane, QUAD4) with a Helmholtz (PDE) filter",
   classification="general example (2-D)",
   role=("Two-dimensional minimum-compliance optimization of an L-bracket: 1 x 1 envelope with the upper-right region "
         "removed (leg width 0.4, re-entrant corner at (0.4, 0.4)), QUAD4 mesh (pave scheme, element size 0.0125) exported "
         "with dimension 2; top edge of the vertical arm (y = 1) clamped in dispx and dispy (nodeset ns_fix); downward "
         "traction (0, -1e5) on the right tip edge x = 1 (sideset ss_load); isotropic elastic, E = 200e9, nu = 0.3; SIMP "
         "minimum value 1e-3; weighted-sum compliance objective; relative volume constraint 0.4 evaluated by the engine "
         "service; Helmholtz filter radius_absolute 0.075 with boundary_sticking_penalty 1.0; density discretization, "
         "initial density 0.5, OC, 30 iterations. A self-contained general example of a 2-D Helmholtz-filter workflow "
         "(geometry, dimension, supports and load type all differ from a 3-D cantilever); it declares no symmetry plane."),
   self_contained="yes: the journal generates the mesh the deck reads; no other example's files or outputs are needed",
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 13 (manual-shipped input deck and journal)",
   files={"topology_mech_ex13.i": "input_deck", "topology_mech_ex13.jou": "journal", "problem_geometry_figure.png": "problem_figure"}),
 "example_16_restart": dict(
   example=16, logical="MORPHORM-CANDIDATE-EX16",
   title="Two-stage restart workflow on the full Helmholtz cantilever",
   classification="restart-specific workflow",
   role=("Restart workflow on the full 2 x 1 x 1 cantilever: stage 1 runs 20 OC iterations with write_restart_file true; "
         "the restart deck runs 40 further iterations starting from the saved design (initial_guess_file_name "
         "initialguess.exo, initial_guess_field_name control, restart_iteration 20). Same physics and filter settings as "
         "the full Helmholtz cantilever; its specific purpose is demonstrating checkpoint/restart of an optimization. "
         "The restart stage needs a stage-1 output (not included)."),
   self_contained=("stage 1 yes (journal + stage-1 deck); the restart stage needs this package's own stage-1 output, "
                   "which a user generates by running stage 1; no other example's files are needed"),
   shipped_from="Morphorm Examples Manual, topology optimization / mechanical, Example 16 (manual-shipped stage-1 deck, restart deck and journal)",
   files={"topology_mech_ex16.i": "stage1_input_deck", "topology_mech_ex16_restart.i": "restart_input_deck",
          "topology_mech_ex16.jou": "journal"}),
}

EX13_README = """# Candidate package example_13 — Morphorm Example 13 (2-D L-bracket, Helmholtz filter)

**Classification:** general example (2-D). **Source:** Morphorm Examples Manual, topology optimization / mechanical, Example 13.
**Source identifier:** `MORPHORM-CANDIDATE-EX13` (logical identifier, not a filesystem path).

Two-dimensional minimum-compliance optimization of an L-shaped bracket. The journal draws a 1 × 1 envelope with the
upper-right region removed (leg width 0.4, re-entrant corner at (0.4, 0.4)), meshes it with QUAD4 elements (pave scheme,
element size 0.0125; the journal's header comment says "structured", but the scheme used is pave) and exports a 2-D
Exodus mesh. The top edge of the vertical arm (y = 1) is clamped in `dispx`/`dispy` (nodeset `ns_fix`); a downward
traction (0, −1e5) acts on the right tip edge x = 1 (sideset `ss_load`). Isotropic elastic material (E = 200e9, ν = 0.3),
SIMP minimum value 1e-3, weighted-sum compliance objective, relative volume constraint 0.4 evaluated by the engine service,
Helmholtz filter (`radius_absolute 0.075`, `boundary_sticking_penalty 1.0`), density discretization with initial density
0.5, OC, 30 iterations. It models the whole domain and declares no symmetry plane.

The package is self-contained: the journal generates the mesh that the deck reads; nothing from another example is needed.

| File (`selected_source_materials/`) | What it is |
|---|---|
| `topology_mech_ex13.i` | shipped input deck |
| `topology_mech_ex13.jou` | shipped Cubit journal |
| `problem_geometry_figure.png` | manual figure of the meshed design domain, clamped edge and loaded edge (no result) |

Omitted: meshes, completed outputs, renders, histories, logs (see `problem_card.yaml`).
"""

ARCHIVE_README = """# E3 CHPC candidate archive (read-only)

Curated, read-only packages of authentic Morphorm example workflows. Each package holds the shipped input files of one
example plus a `README.md`, a machine-readable `problem_card.yaml` (scientific role, classification, included files,
omitted result categories, hashes) and a `provenance.yaml` (logical source identifier and checksum of every file).

| Package | Example | Classification | Content |
|---|---|---|---|
| `example_01/` | 1 | general example | bracket deck, journal, geometry figure |
| `example_07/` | 7 | distinct workflow | full Helmholtz-filter cantilever deck, journal, geometry figure |
| `example_13/` | 13 | general example (2-D) | 2-D L-bracket Helmholtz-filter deck, journal, geometry figure |
| `example_16_restart/` | 16 | restart-specific workflow | stage-1 deck, restart deck, journal |

None of these packages contains completed results (Exodus outputs, renders, histories, logs, accepted summaries).
Whether, and how, any of them is useful for a given task is for the reader to judge from the packages themselves.
`MANIFEST.sha256` lists every file in the archive; verify with `sha256sum -c MANIFEST.sha256` from this directory.

Source identifiers such as `MORPHORM-CANDIDATE-EX07` are logical identifiers. They are not filesystem paths and they are
not the original locations of the files; original locations are kept in researcher-side provenance records only.
"""

def set_writable(on):
    for root, dirs, files in os.walk(CA):
        os.chmod(root, 0o755 if on else 0o555)
        for f in files:
            os.chmod(os.path.join(root, f), 0o644 if on else 0o444)

def write(path, text):
    with open(path, "w") as f:
        f.write(text)

def main():
    rows = list(csv.DictReader(open(E3 + "/setup/source_inventory.csv")))
    by_dest = {r["e3_destination"]: r for r in rows}
    os.makedirs(PROV, mode=0o700, exist_ok=True)
    os.makedirs(REM, exist_ok=True)
    set_writable(True)
    try:
        # ---- copy Example 13
        dst_root = CA + "/example_13/selected_source_materials"
        os.makedirs(dst_root, exist_ok=True)
        ex13_inv = []
        for orig, also, name, ftype, role, fid in EX13:
            dst = dst_root + "/" + name
            if os.path.exists(dst):
                sys.exit(f"refusing to overwrite existing {dst}")
            so = sha(orig)
            if also and sha(also) != so:
                sys.exit(f"identical-copy check failed: {also}")
            shutil.copy2(orig, dst)
            sd = sha(dst)
            if sd != so:
                sys.exit(f"copy hash mismatch for {name}")
            r = dict(original_canonical_path=orig, source_example="13", filename=os.path.basename(orig), file_type=ftype,
                     size_bytes=str(os.path.getsize(orig)), sha256=so, intended_e3_role=role, visibility="agent-visible",
                     e3_destination=dst, identical_copy_also_at=also)
            ex13_inv.append(r)
            by_dest[dst] = r
        write(CA + "/example_13/README.md", EX13_README)
        with open(REM + "/remediation_source_inventory.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(ex13_inv)
        write(REM + "/remediation_source_inventory.sha256",
              "".join(f"{r['sha256']}  {r['original_canonical_path']}\n" for r in ex13_inv)
              + "".join(f"{r['sha256']}  {r['identical_copy_also_at']}\n" for r in ex13_inv if r["identical_copy_also_at"]))

        # ---- cards, provenance, canonical map
        mp = [["logical_source_id", "agent_visible_path_e3_relative", "canonical_original_path",
               "identical_copy_also_at", "sha256", "size_bytes", "note"]]
        for pkg, m in PKG.items():
            root = f"{CA}/{pkg}"
            files = []
            for dirpath, _, fns in os.walk(root + "/selected_source_materials"):
                for fn in sorted(fns):
                    p = os.path.join(dirpath, fn)
                    r = by_dest.get(p)
                    if r is None:
                        sys.exit(f"no inventory record for {p}")
                    if sha(p) != r["sha256"]:
                        sys.exit(f"package file differs from its inventory hash: {p}")
                    files.append((p, r))
            files.sort(key=lambda t: t[0])
            card = [f"# Problem card — E3 candidate package {pkg} (regenerated {NOW} by E3 remediation; logical source identifiers)",
                    f"package_id: {pkg}",
                    f"source_example_number: {m['example']}",
                    f"source_identifier: {m['logical']}",
                    "source_identifier_note: \"logical identifier assigned by E3; it is not a filesystem path and not the original location\"",
                    f"title: {q(m['title'])}",
                    f"classification: {q(m['classification'])}",
                    f"scientific_role: {q(m['role'])}",
                    f"self_contained: {q(m['self_contained'])}",
                    f"shipped_from: {q(m['shipped_from'])}",
                    "authenticity: \"files are byte-identical copies of the original example files (SHA-256 verified at copy time)\"",
                    "contains_completed_results: false",
                    "source_file_identifiers:"]
            for p, r in files:
                card.append(f"  - {m['logical']}/{m['files'][os.path.basename(p)]}")
            card.append("included_files:")
            for p, r in files:
                rel = os.path.relpath(p, root)
                card += [f"  - path: {rel}", f"    source_file_identifier: {m['logical']}/{m['files'][os.path.basename(p)]}",
                         f"    role: {q(r['intended_e3_role'])}", f"    file_type: {q(r['file_type'])}",
                         f"    size_bytes: {r['size_bytes']}", f"    sha256: {r['sha256']}"]
            card.append("omitted_result_categories:")
            card += [f"  - {q(o)}" for o in OMITTED]
            card.append("hashes:")
            for p, r in files:
                card.append(f"  {os.path.relpath(p, root)}: {r['sha256']}")
            write(root + "/problem_card.yaml", "\n".join(card) + "\n")

            prov = [f"# Provenance — E3 candidate package {pkg} (regenerated {NOW} by E3 remediation)",
                    f"package_id: {pkg}", f"source_example_number: {m['example']}", f"source_identifier: {m['logical']}",
                    "curation_method: \"read-only copy of each selected original example file; SHA-256 of original and copy compared; originals never modified\"",
                    "original_locations: \"withheld from agent-visible storage; the mapping from source identifiers to original locations is a researcher-side record\"",
                    "files:"]
            for p, r in files:
                prov += [f"  - destination: {os.path.relpath(p, root)}",
                         f"    source_file_identifier: {m['logical']}/{m['files'][os.path.basename(p)]}",
                         f"    sha256: {r['sha256']}", f"    size_bytes: {r['size_bytes']}"]
                mp.append([f"{m['logical']}/{m['files'][os.path.basename(p)]}", os.path.relpath(p, E3),
                           r["original_canonical_path"], r["identical_copy_also_at"], r["sha256"], r["size_bytes"],
                           "candidate archive (replacement curated at remediation)" if pkg == "example_13" else "candidate archive"])
            write(root + "/provenance.yaml", "\n".join(prov) + "\n")

        write(CA + "/README.md", ARCHIVE_README)
        man = []
        for dirpath, _, fns in os.walk(CA):
            for fn in fns:
                p = os.path.join(dirpath, fn)
                if p != CA + "/MANIFEST.sha256":
                    man.append((sha(p), "./" + os.path.relpath(p, CA)))
        man.sort(key=lambda t: t[1])
        write(CA + "/MANIFEST.sha256", "".join(f"{h}  {p}\n" for h, p in man))
    finally:
        set_writable(False)

    # ---- Globus-tree sources (manuals, target figure) and the docs tree, for the researcher-side map
    extra = {
        "globus_source_root/manuals/Morphorm_User_Manual.pdf": ("MORPHORM-MANUAL-USER-V1", "private source collection (manual)"),
        "globus_source_root/manuals/Morphorm_Theory_Manual.pdf": ("MORPHORM-MANUAL-THEORY-V1", "private source collection (manual)"),
        "globus_source_root/target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png":
            ("MORPHORM-TARGET-SUPPORT-V1/problem_figure", "private source collection (task problem-statement figure)"),
    }
    for r in rows:
        rel = os.path.relpath(r["e3_destination"], E3) if r["e3_destination"].startswith(E3) else ""
        if rel in extra:
            lid, note = extra[rel]
            mp.append([lid, rel, r["original_canonical_path"], r["identical_copy_also_at"], r["sha256"], r["size_bytes"], note])
    mp.append(["MORPHORM-DOCS-SOURCE-V1", "(not copied; referenced in globus_source_root/documentation/version_provenance.yaml)",
               D + "/Morphorm/docs", "", "", "", "documentation source tree, git f07a712bd5ef2b548f870c8f49869e7ec9508f6d (not included in any collection)"])
    mp.append(["MORPHORM-CANDIDATE-EX02 (withdrawn)", "setup/preexisting_state/example_02_incomplete_candidate/ (archived; not agent-visible)",
               DOCS_MECH + "/topology_mech_ex2.i", "", "d060e336bf540d8e2dbe3f524f75c5f7bd48e5449eee06713edf2c0882bcc14a", "",
               "withdrawn at remediation: not self-contained (needs Example 1 mesh and engine output)"])
    with open(PROV + "/agent_visible_to_canonical_source_map.tsv", "w") as f:
        for row in mp:
            f.write("\t".join(row) + "\n")
    os.chmod(PROV + "/agent_visible_to_canonical_source_map.tsv", 0o600)
    print(f"done {NOW}: {len(mp) - 1} mapping rows")

if __name__ == "__main__":
    main()
