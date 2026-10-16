#!/usr/bin/env bash
# Sequential Globus staging of private-source files needed for the task (helper transfers MANIFEST.sha256 first).
H=$E3_TRIAL_ROOT/agent-inputs/control/scripts/non_destructive_preflight_helpers
for p in README.md documentation/curated_readme.md documentation/MANIFEST_README.md documentation/version_provenance.yaml \
         documentation/curated_permitted_materials/software_contract.md documentation/curated_permitted_materials/compute_resources.md \
         target_materials/symmetry_plane_cantilever/README.md target_materials/symmetry_plane_cantilever/problem_specification.md \
         target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png target_materials/symmetry_plane_cantilever/permitted_starting_materials/README.md \
         manuals/Morphorm_User_Manual.pdf; do
  echo "== $(date -u +%FT%TZ) staging $p"; "$H/globus_stage_file.sh" "$p" || echo "FAILED: $p"
done
echo "== $(date -u +%FT%TZ) done"
