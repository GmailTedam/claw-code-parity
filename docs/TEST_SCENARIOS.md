# Test Scenarios — Cross-Repository Enhancement from Claw-Code-Parity

Date: 2026-04-05

## Part A — BulletTrain Slash Commands (Implemented)

| TEST-ID | Traces | Scenario | Input | Expected |
|---------|--------|----------|-------|----------|
| TS-001 | REQ-BT-011 | All 15 new commands are registered in SLASH_COMMAND_SPECS | `slash_command_specs()` | Returns 41 specs (26 existing + 15 new) |
| TS-002 | REQ-BT-002 | Each new command has valid metadata | Iterate specs | All have non-empty name, summary; argument_hint present where expected |
| TS-003 | REQ-BT-003 | Healthcare commands (`/registry`, `/a2a`, `/fhir`) are feature-gated | Check source field | Future: `source == FeatureGated` |
| TS-004 | REQ-BT-004 | Scaffold validates field syntax | `/scaffold Foo bad_field` | Returns validation error for missing colon separator |
| TS-005 | REQ-BT-004 | Scaffold accepts valid fields | `/scaffold Foo name:string age:integer` | Returns success with parsed field list |
| TS-006 | REQ-BT-001 | Command names follow namespace pattern | All new specs | Names match `[a-z][a-z0-9:_-]*` |
| TS-007 | REQ-BT-009 | Audit supports time filtering | `/audit log --since=7d` | Parses duration, returns filtered results |
| TS-008 | REQ-BT-010 | Webhook validates URL | `/webhook create not-a-url` | Returns URL validation error |
| TS-009 | REQ-BT-013 | Python snapshot includes new commands | `load_command_snapshot()` | Contains scaffold, team, roles, api, billing, action, webhook, audit, theme, db, registry, a2a, fhir entries |
| TS-010 | REQ-BT-012 | All new enum variants parse correctly | `/scaffold Patient`, `/team list`, `/db migrate`, etc. | Each returns correct `SlashCommand` variant |
| TS-011 | REQ-BT-012 | Alias resolution works | `/webhooks list`, `/database seed` | Resolves to `Webhook` and `Db` respectively |
| TS-012 | REQ-BT-002 | Resume-supported commands are correctly flagged | `resume_supported_slash_commands()` | Returns 16 specs (14 existing + audit + registry) |
| TS-013 | REQ-BT-012 | New commands are runtime-bound (return None from handle_slash_command) | All 15 new commands | `handle_slash_command` returns `None` |

### Rust Test Implementation

All scenarios TS-001, TS-002, TS-006, TS-010, TS-011, TS-012, TS-013 are implemented in `rust/crates/commands/src/lib.rs` within the `#[cfg(test)]` module:

- `parses_supported_slash_commands` — covers TS-010, TS-011
- `renders_help_from_shared_specs` — covers TS-001, TS-002, TS-006, TS-012
- `ignores_unknown_or_runtime_bound_slash_commands` — covers TS-013

## Part B — Global Agent Registry

| TEST-ID | Traces | Scenario | Input | Expected |
|---------|--------|----------|-------|----------|
| TS-GAR-001 | REQ-GAR-001 | Register agent with valid manifest | POST `/v1/agents` with full manifest | 201 Created |
| TS-GAR-002 | REQ-GAR-002 | Register agent with missing capabilities | POST with empty capabilities array | 400 Bad Request |
| TS-GAR-003 | REQ-GAR-003 | Register duplicate agent name | POST same agent name twice | 409 Conflict |
| TS-GAR-004 | REQ-GAR-002 | Register agent with invalid crypto material | POST with expired certificate | 400 Bad Request |
| TS-GAR-005 | REQ-GAR-004 | Discover agents by capability | GET `/v1/discover?capability=triage` | Returns matching agents |
| TS-GAR-006 | REQ-GAR-005 | Discovery includes cache signatures | GET discover | ETag header present |
| TS-GAR-007 | REQ-GAR-006 | Discover with jurisdiction filter | GET `/v1/discover?jurisdiction=EU` | Only EU agents returned |
| TS-GAR-008 | REQ-GAR-004 | Discover non-existent capability | GET `/v1/discover?capability=nonexistent` | 200 with empty result set |
| TS-GAR-009 | REQ-GAR-007 | Agent with deny rule is blocked | Trust verify for denied agent | Denied with reason |
| TS-GAR-010 | REQ-GAR-007 | Agent with allow rule and valid trust is permitted | Trust verify for allowed agent | Permitted |
| TS-GAR-011 | REQ-GAR-009 | Break-glass override | Emergency access request | Permitted + audit entry created |
| TS-GAR-012 | REQ-GAR-008 | Wildcard rule matching | Rule `triage.*` vs agent `triage.ed.intake` | Matches |
| TS-GAR-013 | REQ-GAR-007 | Expired trust certificate | Verify agent with expired cert | Denied |
| TS-GAR-014 | REQ-GAR-010 | Root deny + Org allow = still denied | Org tries to override Root deny | Denied |
| TS-GAR-015 | REQ-GAR-011 | Sovereign overrides Root within jurisdiction | Sovereign sets jurisdiction restriction | Sovereign policy applies |
| TS-GAR-016 | REQ-GAR-012 | Org cannot weaken Sovereign deny | Org attempts to allow denied agent | Deny preserved |
| TS-GAR-017 | REQ-GAR-010 | Org adds local trust policy | Org adds allow rule | Merged with higher layers |

## Part C — Nexus A2A Protocol

| TEST-ID | Traces | Scenario | Input | Expected |
|---------|--------|----------|-------|----------|
| TS-N2A-001 | REQ-N2A-001 | All 13 admission checks pass | Valid agent request | Route admitted |
| TS-N2A-002 | REQ-N2A-003 | Admission check 3 (namespace delegation) fails | Invalid namespace | Rejected with point=3 |
| TS-N2A-003 | REQ-N2A-003 | Admission check 9 (jurisdiction) fails | Wrong jurisdiction | Rejected with data-residency error |
| TS-N2A-004 | REQ-N2A-004 | Abort signal during admission check 7 | Cancel signal sent | Graceful cancellation |
| TS-N2A-005 | REQ-N2A-005 | Progress reporter receives updates | Full 13-point admission | 13 progress updates received |
| TS-N2A-006 | REQ-N2A-006 | Simple task lifecycle | Accept -> Complete | Task completes normally |
| TS-N2A-007 | REQ-N2A-006 | Complex task with checkpoints | Accept -> Checkpoint -> Checkpoint -> Complete | All checkpoints persisted |
| TS-N2A-008 | REQ-N2A-006 | Failed task | Accept -> Reject | Error details preserved |
| TS-N2A-009 | REQ-N2A-006 | Escalation task | Accept -> Escalate | Context preserved for human |
| TS-N2A-010 | REQ-N2A-008 | Long conversation auto-compaction | Input tokens > threshold | Compaction triggers, history preserved |
| TS-N2A-011 | REQ-N2A-010 | Triage agent subprocess | ED intake FHIR payload | Returns triage category via stdout |
| TS-N2A-012 | REQ-N2A-010 | Agent timeout | Agent hangs > 30s | Process killed, task marked failed |
| TS-N2A-013 | REQ-N2A-012 | Agent returns malformed JSON | Invalid stdout | Error captured, task rejected |
| TS-N2A-014 | REQ-N2A-013 | Environment variables set correctly | Each of 25 agents | AGENT_ID, TASK_ID, PATIENT_CONTEXT_HASH present |
| TS-N2A-015 | REQ-N2A-014 | Single exchange persisted | One A2A exchange | JSONL file created with correct schema |
| TS-N2A-016 | REQ-N2A-015 | Forked conversation | Fork a session | parent_session_id populated |
| TS-N2A-017 | REQ-N2A-016 | Session rotation | Session exceeds 256KB | Rotation to new file |
| TS-N2A-018 | REQ-N2A-017 | Tamper detection | Modified JSONL record | Validation failure |
| TS-N2A-019 | REQ-N2A-018 | Agent configured for Bevan | Bevan-configured agent | Routes to local endpoint |
| TS-N2A-020 | REQ-N2A-018 | Agent configured for Claude | Claude-configured agent | Routes to Anthropic API |
| TS-N2A-021 | REQ-N2A-020 | Provider failover | Primary provider down | Failover to secondary |
| TS-N2A-022 | REQ-N2A-019 | Patient data forced to Bevan | Payload contains patient data | Forced to Bevan regardless of config |
