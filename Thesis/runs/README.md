# Trial packets

`E1_uninterrupted_example8/baseline/trial_01..05` and `E2_interrupted_recovery_example16/baseline/trial_01..05` are planned baseline
packets; `E3_disparate_storage_example8/baseline/trial_01..05` are planned, non-executable packets. `*/clio/` is reserved (not implemented).
Each packet: `manifest.yaml` (status: planned, null curation/scoring), `agent_inputs/` (frozen documents + two manuals), and empty
`work/ jobs/ logs/ outputs/` (`.gitkeep` only). Verify with `automation/verify_trial_packet.sh --trial-dir <packet> --planned`.
