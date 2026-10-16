# Headless Claude Code syntax (verified, not guessed)

The launcher uses only flags that `preflight.sh` finds in the pinned executable's own `--help` output. **Update 2026-10-09:** the researcher repinned the baseline to `$HOME/.local/share/claude/versions/2.1.295` because 2.1.292 was not installed.
The syntax below was verified against 2.1.295's own `--help`; `preflight.sh` re-reads `--help` on every run.

```
claude --print --verbose --output-format stream-json --model claude-fable-5-1 --dangerously-skip-permissions \
       --session-id <uuid> --disable-slash-commands --no-chrome -- "<prompt text>"
```

| Flag | From `--help` | Why |
|---|---|---|
| `-p, --print` | "Print response and exit (useful for pipes)" | non-interactive run |
| `--output-format stream-json` | "stream-json (realtime streaming)" (only with --print) | complete machine-readable event stream, captured to `stream.jsonl` |
| `--verbose` | "Override verbose mode setting" | full tool/assistant events in the stream |
| `--model <model>` | "Model for the current session … or a model's full name" | `claude-fable-5-1` |
| `--dangerously-skip-permissions` | "Bypass all permission checks" | there is no human to answer permission prompts |
| `--session-id <uuid>` | "Use a specific session ID for the conversation (must be a valid UUID)" | known transcript name; distinct per session |
| `--disable-slash-commands`, `--no-chrome` | present | no skills/plugins or browser integration in trials |
| `-- "<prompt>"` | positional `[prompt]` | the exact prompt file content |

Environment: `DISABLE_AUTOUPDATER=1`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`,
`CLAUDE_CONFIG_DIR=Thesis/.agent_runtime/<run_id>/<label>/claude_config` (per session), `THESIS_TRIAL_ID=<run id>`; all inherited `CLAUDE*` variables are removed. Transcript:
`$CLAUDE_CONFIG_DIR/projects/<cwd-slug>/<session-id>.jsonl` (copied into the evidence directory after the run).
Authentication without a model call: `claude auth status --json` (checked by preflight and again inside the isolated config dir).

Never used: `--resume/-r`, `--continue/-c`, `--fork-session`, `--teleport`, `--from-pr`, `--bg/--background`, `--cloud`, `--bare`
(`--bare` would disable OAuth login, which is the researcher's provider route).
