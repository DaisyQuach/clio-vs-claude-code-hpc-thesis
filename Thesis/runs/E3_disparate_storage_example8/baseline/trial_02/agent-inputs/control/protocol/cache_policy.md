# Cache policy

1. No cross-trial reuse. Every trial starts with an empty staging directory and an empty workspace; nothing staged,
   generated or downloaded in another trial may be read or reused.
2. No persistent caches for scientific material. Do not place staged or generated scientific files in home-directory caches,
   shared scratch, or any location outside the trial root and `$E3_STAGING_DIR`.
3. Within a trial, a staged file may be reused as long as its SHA-256 still equals the recorded source SHA-256. Re-stage
   (and record it again) if verification fails.
4. Tool caches created implicitly by approved software (for example compiler or Python bytecode caches) are not scientific
   inputs; do not rely on them across trials.
5. The control repository is used at the commit recorded in `agent-inputs/CONTROL_COMMIT.txt` only.
