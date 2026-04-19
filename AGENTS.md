# AGENTS.md — claw-code-parity

Harness-neutral entry point for OpenAI Codex, Aider, Cursor, shell operators, and CI runners.
For Claude Code sessions the primary instruction file is [CLAUDE.md](CLAUDE.md).

## No Emoji Policy

No emoji in any code, output, log, or documentation — in any language.

- NO emoji in Rust: `println!()`, `eprintln!()`, comments, doc-comments
- NO emoji in Markdown, JSON, TOML, YAML, shell scripts
- NO emoji in terminal output or CI logs

ASCII status markers: `[OK]` `[FAIL]` `[WARN]` `[INFO]` `[ERROR]` `[SUCCESS]` `[SKIP]` `[PENDING]`

## Quick Reference

### Setup

```bash
cd rust
cargo build
```

### Lint

```bash
cd rust
cargo fmt
cargo clippy --workspace --all-targets -- -D warnings
```

### Test

```bash
cd rust
cargo test --workspace
```

### Notes

- Active implementation lives in `rust/` (Rust workspace).
- `src/` and `tests/` contain artefacts that must stay aligned with `rust/` behaviour.
- Keep shared defaults in `.claude.json`; machine-local overrides go in `.claude/settings.local.json`.
