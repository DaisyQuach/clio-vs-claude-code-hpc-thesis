# E3 baseline trial_01

The only valid agent-visible input packet for this trial is **`agent-inputs/`** (the E3 packet, generated before launch by
the E3 preparation step). There is no other input packet in this trial directory.

An earlier, pre-E3 planning packet that used to sit here has been archived outside the trial directory and is not part of
this trial. The legacy fields at the top of `manifest.yaml` (`frozen_configuration_id`, `frozen_configuration_sha256`,
`agent_inputs_sha256`) are retained only as history and describe that archived packet, not `agent-inputs/`; the
`e3dc_*` and `e3rem_*` fields describe this E3 trial.

Status: planned. Not yet cleared for a counted run.
