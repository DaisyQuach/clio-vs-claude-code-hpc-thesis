#!/usr/bin/env python3
"""E3 curation: copy selected read-only originals into the E3 root (never modifies a source) and build the inventory."""
import csv, hashlib, os, shutil, sys

D = "/uufs/chpc.utah.edu/common/home/chet/Daisy"
E3 = D + "/Thesis/runs/E3_disparate_storage_example8"
MFET = D + "/Morphorm_Full_Examples_Tests"
MGT = D + "/Morphorm_ground_truth"
DOCS = D + "/Morphorm/docs"
MECH = DOCS + "/examples/input_decks/topology_optimization/mech"
FIGS = DOCS + "/examples/figs/topology_optimization/mech"
MAN = D + "/morphorm_manuals"
CA = E3 + "/chpc_candidate_archive"
GS = E3 + "/globus_source_root"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def ftype(p):
    ext = os.path.splitext(p)[1].lower()
    return {".i": "Morphorm input deck (text)", ".jou": "Coreform Cubit journal (text)", ".png": "PNG image",
            ".pdf": "PDF document", ".exo": "Exodus II (binary)", ".txt": "text", ".md": "Markdown", ".csv": "CSV",
            ".json": "JSON", ".py": "Python source", ".inc": "reStructuredText include", ".xml": "XML",
            ".out": "Slurm stdout log", ".sbatch": "Slurm script", ".log": "log (text)"}.get(ext, "other")

# (original, example, destination or None, role, visibility, identical-copy note)
COPIES = [
    (MFET + "/topology_mech_ex1.i", "1", CA + "/example_01/selected_source_materials/topology_mech_ex1.i",
     "candidate input deck (Example 1, as shipped)", "agent-visible", MECH + "/topology_mech_ex1.i"),
    (MECH + "/topology_mech_ex1.jou", "1", CA + "/example_01/selected_source_materials/topology_mech_ex1.jou",
     "candidate mesh-generation journal (Example 1, as shipped)", "agent-visible", ""),
    (FIGS + "/topology_original_geom_mech_ex1.png", "1", CA + "/example_01/selected_source_materials/problem_geometry_figure.png",
     "problem-statement geometry/mesh figure (no result)", "agent-visible", ""),
    (MECH + "/topology_mech_ex2.i", "2", CA + "/example_02/selected_source_materials/topology_mech_ex2.i",
     "candidate input deck (Example 2, as shipped)", "agent-visible", ""),
    (MFET + "/Example7_Helmholtz/topology_mech_ex7.i", "7", CA + "/example_07/selected_source_materials/topology_mech_ex7.i",
     "candidate input deck (Example 7, as shipped)", "agent-visible", MECH + "/topology_mech_ex7.i"),
    (MFET + "/Example7_Helmholtz/topology_mech_ex7.jou", "7", CA + "/example_07/selected_source_materials/topology_mech_ex7.jou",
     "candidate mesh-generation journal (Example 7, as shipped)", "agent-visible", MECH + "/topology_mech_ex7.jou"),
    (FIGS + "/topology_original_geom_mech_ex7.png", "7", CA + "/example_07/selected_source_materials/problem_geometry_figure.png",
     "problem-statement geometry/mesh figure (no result)", "agent-visible", ""),
    (MFET + "/Example16_Restart/topology_mech_ex16.i", "16", CA + "/example_16_restart/selected_source_materials/topology_mech_ex16.i",
     "candidate stage-1 input deck (Example 16, as shipped)", "agent-visible", MECH + "/topology_mech_ex16.i"),
    (MFET + "/Example16_Restart/topology_mech_ex16_restart.i", "16", CA + "/example_16_restart/selected_source_materials/topology_mech_ex16_restart.i",
     "candidate restart input deck (Example 16, as shipped)", "agent-visible", MECH + "/topology_mech_ex16_restart.i"),
    (MFET + "/Example16_Restart/topology_mech_ex16.jou", "16", CA + "/example_16_restart/selected_source_materials/topology_mech_ex16.jou",
     "candidate mesh-generation journal (Example 16, as shipped)", "agent-visible", MECH + "/topology_mech_ex16.jou"),
    (MAN + "/usermanual.pdf", "manual", GS + "/manuals/Morphorm_User_Manual.pdf",
     "permitted documentation (private Globus source only; never GitHub)", "agent-visible (private)", ""),
    (MAN + "/theorymanual.pdf", "manual", GS + "/manuals/Morphorm_Theory_Manual.pdf",
     "permitted documentation (private Globus source only; never GitHub)", "agent-visible (private)", ""),
    (FIGS + "/topology_original_geom_mech_ex8.png", "8 (problem statement only)", GS + "/target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png",
     "target problem-statement figure: half domain, mesh, supports, load, symmetry plane (no result)", "agent-visible", MGT + "/Example_08/original_inputs/manual_figures/topology_original_geom_mech_ex8.png"),
]

# researcher-only: inventory/provenance record only, never copied into agent-visible storage
POINTERS = [
    (MFET + "/Example8_SymmetryPlane/topology_mech_ex8.i", "8", "completed Example 8 input deck (target solution)"),
    (MFET + "/Example8_SymmetryPlane/topology_mech_ex8.jou", "8", "completed Example 8 journal (target solution)"),
    (MFET + "/Example8_SymmetryPlane/topology_mech_ex8.exo", "8", "completed Example 8 mesh"),
    (MFET + "/Example8_SymmetryPlane/run_morphorm_ex8.sbatch", "8", "completed Example 8 job script"),
    (MFET + "/Example8_SymmetryPlane/morphorm-ex8-groundtruth.16053535.out", "8", "Example 8 solver log"),
    (MFET + "/Example8_SymmetryPlane/README.md", "8", "Example 8 result summary"),
    (MECH + "/topology_mech_ex8.i", "8", "Example 8 shipped deck (docs tree original)"),
    (MECH + "/topology_mech_ex8.jou", "8", "Example 8 shipped journal (docs tree original)"),
    (DOCS + "/examples/topology_optimization/mech/examples_topology_optimization_mech_ex8.inc", "8", "Examples Manual Example 8 page source (contains completed listings)"),
    (FIGS + "/topology_opt_mech_ex8.png", "8", "Example 8 optimized topology figure (result)"),
    (MGT + "/Example_08/GROUND_TRUTH_INDEX.md", "8", "Example 8 ground-truth index"),
    (MGT + "/Example_08/provenance/SHA256SUMS.txt", "8", "Example 8 ground-truth package hash manifest"),
    (MGT + "/Example_08/reference_run/engine_output.exo", "8", "Example 8 reference engine output"),
    (MGT + "/Example_08/reference_run/morphorm_oc_optimizer_diagnostics.txt", "8", "Example 8 reference optimizer history"),
    (MGT + "/Example_08/scalar_results/example08_summary.json", "8", "Example 8 reference scalar summary"),
    (MGT + "/Example_08/figures/Example_08_final_topology_iteration50.png", "8", "Example 8 reference topology render"),
    (MAN + "/examplesmanual.pdf", "manual", "Examples Manual (contains completed Example 8 listings)"),
]

def main():
    inv, sums = [], []
    for src, ex, dst, role, vis, ident in COPIES:
        assert os.path.isfile(src), src
        h = sha(src)
        if ident:
            assert sha(ident) == h, ("identical-copy claim failed", ident)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            assert sha(dst) == h, ("destination exists with different content", dst)
        else:
            shutil.copy2(src, dst)            # read-only use of the original
        assert sha(dst) == h, ("copy verification failed", dst)
        inv.append(dict(original_canonical_path=src, source_example=ex, filename=os.path.basename(src), file_type=ftype(src),
                        size_bytes=os.path.getsize(src), sha256=h, intended_e3_role=role, visibility=vis,
                        e3_destination=dst, identical_copy_also_at=ident))
        sums.append(f"{h}  {src}")
    for src, ex, role in POINTERS:
        assert os.path.isfile(src), src
        h = sha(src)
        inv.append(dict(original_canonical_path=src, source_example=ex, filename=os.path.basename(src), file_type=ftype(src),
                        size_bytes=os.path.getsize(src), sha256=h, intended_e3_role=role + " -- inventory record only, not copied",
                        visibility="researcher-only", e3_destination="(none; recorded in researcher_only/example8_reference/)",
                        identical_copy_also_at=""))
        sums.append(f"{h}  {src}")
    with open(E3 + "/setup/source_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(inv[0].keys()))
        w.writeheader(); w.writerows(inv)
    with open(E3 + "/setup/source_inventory.sha256", "w") as f:
        f.write("\n".join(sums) + "\n")
    print(f"{len(COPIES)} files curated, {len(POINTERS)} researcher-only records")

if __name__ == "__main__":
    main()
