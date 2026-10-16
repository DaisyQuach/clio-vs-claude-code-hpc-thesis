# E3 baseline trial_04

The only valid agent-visible input packet for this trial is **`agent-inputs/`** (the E3 packet, generated before launch by
the E3 preparation step; empty until then). There is no other input packet in this trial directory.

An earlier, pre-E3 planning packet that used to sit here has been archived outside the trial directory and is not part of
this trial. The legacy fields at the top of `manifest.yaml` (`frozen_configuration_id`, `frozen_configuration_sha256`,
`agent_inputs_sha256`) are retained only as history and describe that archived packet, not `agent-inputs/`; the
`e3dc_*` and `e3proc_*` fields describe this E3 trial.

Access policy (same as Experiments 1 and 2): use only your own trial workspace, the collections listed in the
control catalog, and the approved software interface. Researcher-only records, other trials and experiments, original
software/source trees, completed reference material, and scoring or validation records are prohibited. They are not in
this trial's input packet. Every path used during the session is recorded and audited after the trial. Because trials
run under the researcher's account, this separation is procedural rather than a technically enforced filesystem
boundary: that a location can be read does not mean it may be read.

Status: planned. Not yet cleared for a counted run.
