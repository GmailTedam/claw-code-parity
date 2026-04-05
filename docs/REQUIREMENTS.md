# Requirements — Cross-Repository Enhancement from Claw-Code-Parity

Date: 2026-04-05

## Part A — BulletTrain Slash Commands (Implemented in this repo)

| REQ-ID | Requirement | Traces To | Priority |
|--------|-------------|-----------|----------|
| REQ-BT-001 | Slash commands SHALL use hierarchical namespacing (`/resource action`) | BT-01 to BT-15 | P1 |
| REQ-BT-002 | Each command SHALL declare aliases, argument hints, and resume support via `SlashCommandSpec` | All new specs | P1 |
| REQ-BT-003 | Commands SHALL be categorized by source (`Builtin`, `FeatureGated`, `InternalOnly`) | `CommandSource` enum | P1 |
| REQ-BT-004 | `/scaffold` commands SHALL validate field type syntax (`name:type`) before execution | BT-01, BT-02, BT-03 | P1 |
| REQ-BT-005 | `/team` and `/roles` SHALL enforce permission checks before mutation | BT-04, BT-05 | P1 |
| REQ-BT-006 | `/registry` SHALL bridge to Global Agent Registry discovery API | BT-13 | P2 |
| REQ-BT-007 | `/a2a` SHALL bridge to Nexus A2A JSON-RPC 2.0 protocol | BT-14 | P2 |
| REQ-BT-008 | `/fhir` SHALL validate against FHIR R4 resource schemas | BT-15 | P2 |
| REQ-BT-009 | `/audit` SHALL support time-range filtering and user filtering | BT-10 | P1 |
| REQ-BT-010 | `/webhook` SHALL validate URL format and support test payloads | BT-09 | P1 |
| REQ-BT-011 | All new commands SHALL be registered in `SLASH_COMMAND_SPECS` static array | All | P1 |
| REQ-BT-012 | All new commands SHALL have corresponding `SlashCommand` enum variants and parser arms | All | P1 |
| REQ-BT-013 | Python `src/reference_data/commands_snapshot.json` SHALL be updated to include new commands | All | P1 |

### Implementation Status

- REQ-BT-001: **Done** — all commands follow `/resource action` pattern
- REQ-BT-002: **Done** — all 15 specs have aliases, argument_hint, resume_supported
- REQ-BT-011: **Done** — `SLASH_COMMAND_SPECS` now has 41 entries (26 existing + 15 new)
- REQ-BT-012: **Done** — `SlashCommand` enum has 15 new variants with parser arms
- REQ-BT-013: **Done** — Python snapshot updated with 15 new entries

## Part B — Global Agent Registry (For symphonix-health/global-agent-registry)

| REQ-ID | Requirement | Source Pattern | Priority |
|--------|-------------|----------------|----------|
| REQ-GAR-001 | Agent registration SHALL accept a manifest with capabilities, endpoints, crypto material | Plugin manifest (`plugins/src/lib.rs`) | P1 |
| REQ-GAR-002 | Registry SHALL validate manifest against JSON Schema before accepting | `PluginManager::install` validation | P1 |
| REQ-GAR-003 | Registry SHALL reject duplicate agent names within same namespace | `GlobalToolRegistry::with_plugin_tools` dedup | P1 |
| REQ-GAR-004 | Discovery SHALL support capability-based search | `route_prompt` token matching | P1 |
| REQ-GAR-005 | Discovery SHALL return content-hash signatures for caching | MCP content-hash signatures | P2 |
| REQ-GAR-006 | Discovery SHALL scope results by jurisdiction | `ConfigSource` scoping | P1 |
| REQ-GAR-007 | Trust verification SHALL follow deny -> hook-override -> allow -> escalate flow | `PermissionPolicy` + `HookRunner` | P1 |
| REQ-GAR-008 | Rules SHALL support wildcard and prefix matching on agent attributes | `RuntimePermissionRuleConfig` | P1 |
| REQ-GAR-009 | Emergency break-glass SHALL bypass normal rules with audit logging | `HookAbortSignal` pattern | P1 |
| REQ-GAR-010 | Config SHALL merge with Root < Sovereign < Organizational precedence | `RuntimeConfig` 3-layer merge | P1 |
| REQ-GAR-011 | Sovereign registries SHALL override Root trust policies within their jurisdiction | `ConfigSource` precedence | P1 |
| REQ-GAR-012 | Organizational registries SHALL not weaken Sovereign deny rules | Deny-rule enforcement | P1 |

## Part C — Nexus A2A Protocol (For symphonix-health/nexus-a2a-protocol)

| REQ-ID | Requirement | Source Pattern | Priority |
|--------|-------------|----------------|----------|
| REQ-N2A-001 | Each of 13 admission points SHALL execute as an independent hook | `HookRunner` pipeline | P1 |
| REQ-N2A-002 | Hooks SHALL receive full request context via stdin JSON | Hook stdin piping | P1 |
| REQ-N2A-003 | Hook failure at any point SHALL abort the route with specific error code | Exit-code signaling | P1 |
| REQ-N2A-004 | Hooks SHALL support `HookAbortSignal` for cancellation | `HookAbortSignal` | P1 |
| REQ-N2A-005 | Hooks SHALL report progress via `HookProgressReporter` | `HookProgressReporter` trait | P2 |
| REQ-N2A-006 | Task execution SHALL follow stateful lifecycle with persistent checkpoints | `ConversationRuntime` loop | P1 |
| REQ-N2A-007 | Execution loop SHALL support streaming via SSE | `api/src/sse.rs` | P1 |
| REQ-N2A-008 | Auto-compaction SHALL apply when conversation exceeds token threshold | `auto_compaction_input_tokens_threshold` | P2 |
| REQ-N2A-009 | Each tool execution SHALL run through route admission hooks | Pre/post tool-use hooks | P1 |
| REQ-N2A-010 | Each clinical agent SHALL execute as an isolated subprocess | `execute_plugin_command` | P1 |
| REQ-N2A-011 | Agent SHALL receive FHIR payload via stdin JSON | Plugin JSON I/O | P1 |
| REQ-N2A-012 | Agent SHALL return structured result via stdout JSON | Plugin JSON I/O | P1 |
| REQ-N2A-013 | Environment variables SHALL expose context (`AGENT_ID`, `TASK_ID`, `PATIENT_CONTEXT_HASH`) | `CLAWD_PLUGIN_ID` etc. | P1 |
| REQ-N2A-014 | All A2A exchanges SHALL be persisted as JSONL session records | JSONL session persistence | P1 |
| REQ-N2A-015 | Sessions SHALL support fork lineage (`parent_session_id`) | Session fork metadata | P1 |
| REQ-N2A-016 | Session rotation SHALL occur at configurable size threshold | 256KB rotation | P2 |
| REQ-N2A-017 | Sessions SHALL be tamper-evident (hash-chained) | New requirement for healthcare | P1 |
| REQ-N2A-018 | Each clinical agent SHALL declare its preferred LLM provider | `ProviderClient` enum | P1 |
| REQ-N2A-019 | Provider selection SHALL respect data-residency rules (Bevan for on-prem patient data) | Provider routing | P1 |
| REQ-N2A-020 | Provider failover SHALL be configurable per agent | Provider abstraction | P2 |

## Traceability Matrix

| Requirement | Use Case | Test Scenario | Implementation File |
|-------------|----------|---------------|---------------------|
| REQ-BT-001 | UC-001 to UC-013 | TS-006 | `rust/crates/commands/src/lib.rs` |
| REQ-BT-002 | UC-001 to UC-013 | TS-002 | `rust/crates/commands/src/lib.rs` |
| REQ-BT-011 | All | TS-001, TS-009 | `rust/crates/commands/src/lib.rs`, `src/reference_data/commands_snapshot.json` |
| REQ-BT-012 | All | TS-010 | `rust/crates/commands/src/lib.rs` |
| REQ-BT-013 | All | TS-009 | `src/commands.py`, `src/reference_data/commands_snapshot.json` |
| REQ-GAR-001 to 012 | — | In GAR manifest | Target: `symphonix-health/global-agent-registry` |
| REQ-N2A-001 to 020 | — | In N2A manifest | Target: `symphonix-health/nexus-a2a-protocol` |
