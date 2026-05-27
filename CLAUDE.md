<!-- global-workspace-instructions:start -->

## Global workspace instructions

Also read and follow `C:\Users\hgeec\github\CLAUDE.md` and `C:\Users\hgeec\github\AGENTS.md` before working in this repository. These repo-local instructions remain in force. If a repo-local instruction conflicts with global files, prefer the more specific repo-local instruction unless a system, developer, or user instruction says otherwise.

<!-- global-workspace-instructions:end -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Detected stack
- Languages: Rust.
- Frameworks: none detected from the supported starter markers.

## Verification
- Run Rust verification from `rust/`: `cargo fmt`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`
- `src/` and `tests/` are both present; update both surfaces together when behavior changes.

## Repository shape
- `rust/` contains the Rust workspace and active CLI/runtime implementation.
- `src/` contains source files that should stay consistent with generated guidance and tests.
- `tests/` contains validation surfaces that should be reviewed alongside code changes.

## Working agreement
- Prefer small, reviewable changes and keep generated bootstrap files aligned with actual repo workflows.
- Keep shared defaults in `.claude.json`; reserve `.claude/settings.local.json` for machine-local overrides.
- Do not overwrite existing `CLAUDE.md` content automatically; update it intentionally when repo workflows change.

## No Emoji Policy

No emoji in any code, output, log, or documentation — in any language.

- NO emoji in Python: `print()`, logging, exceptions, comments, docstrings
- NO emoji in TypeScript/JavaScript: `console.log`, JSX, strings
- NO emoji in Markdown, JSON, YAML, TOML, HTML, CSS
- NO emoji in terminal commands or shell output

ASCII status markers: `[OK]` `[FAIL]` `[WARN]` `[INFO]` `[ERROR]` `[SUCCESS]` `[SKIP]` `[PENDING]`
