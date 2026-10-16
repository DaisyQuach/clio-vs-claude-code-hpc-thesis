# Curated documentation

This collection deliberately contains only what is needed to understand the permitted input-deck syntax, the execution
environment and the workflow constraints. The full Morphorm documentation source tree is **not** included.

| File | Purpose |
|---|---|
| `../manuals/Morphorm_User_Manual.pdf` | input-deck syntax (blocks, keywords), XMLGenerator workflow |
| `../manuals/Morphorm_Theory_Manual.pdf` | formulation background (SIMP, filters, optimizers) |
| `curated_permitted_materials/software_contract.md` | the approved software interface (Morphorm runtime, Cubit) and its commands |
| `curated_permitted_materials/compute_resources.md` | the frozen Slurm resource contract |
| `version_provenance.yaml` | versions and checksums of the documentation and software referenced here |

Curation rationale: the User Manual already documents every input-deck block; the source tree adds build tooling,
examples and rendered example outputs, which are outside the permitted material for this task.
