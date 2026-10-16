# Formal Configuration (frozen)

| Field | Frozen value |
|---|---|
| Frozen configuration ID | `FROZEN-EX8-v1` (hash in `FROZEN_CONFIG_SHA256.txt`) |
| Workflow | Half cantilever with a Helmholtz symmetry-plane filter (`scientific_problem_specification.md`) |
| Model | `claude-fable-5-1` (Claude Code subscription route; harness defaults; no temperature, token-limit or effort overrides) |
| Agent harness | Claude Code `2.1.295`, fully headless (`--print`), new process per session, no resume/continue/fork, autoupdater disabled |
| Morphorm runtime | `morphorm/approved-runtime` (engine 0d767ac7, analyze 60c5e37c; modulefile SHA-256 `dec9d78b15cd0a5925f9e4907bce8f0f9d6c9859c24e952e51e8a849bc93e58d`; inventory SHA-256 `fa0d97b93a7990271813eccf8768e14465266853a83ef8adab9e6987b4e3e4d2`) with CHPC `gcc/11.2.0`, `openmpi/5.0.3` |
| Mesher | Coreform Cubit 2026.8 (`cubit-edu/2026.8`, modulefile SHA-256 `9c5bc2f9e266616ceebd384d82d0859d9977e0085635053061652728704819ad`) |
| Software interface | `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` |
| Morphorm job resources | account `hochhalter-np`, partition `hochhalter-np`, 1 node, 1 task × 8 CPUs, 32 GB, 02:00:00, no GPU |
| Agent-host resources | same partition/account, 1 node, 8 CPUs, 32 GB, 02:00:00 |
| Network policy | model-provider communication and CHPC scheduler/module access only; no web search, downloads, or external reference retrieval |
| Fresh-session policy | every session is a newly started Claude Code process in a distinct trial workspace; no conversation, memory, artifact or job is reused between trials |
| Permitted documentation | `manuals/Morphorm_User_Manual.pdf`, `manuals/Morphorm_Theory_Manual.pdf` |
