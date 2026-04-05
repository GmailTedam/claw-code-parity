# Use Cases — Cross-Repository Enhancement from Claw-Code-Parity

Date: 2026-04-05

## Part A — BulletTrain Slash Commands

| UC-ID | Actor | Action | Expected Outcome | Traces To |
|-------|-------|--------|------------------|-----------|
| UC-001 | Developer | `/scaffold Patient name:string dob:date mrn:string` | Generates model, controller, views, API endpoint, and tests for Patient | REQ-BT-004 |
| UC-002 | Developer | `/scaffold:api Appointment` | Generates API-only scaffold without views | REQ-BT-004 |
| UC-003 | Developer | `/scaffold:join Patient Provider` | Generates join model with belongs_to associations | REQ-BT-004 |
| UC-004 | Team Admin | `/team invite doctor@hospital.org --role=clinician` | Sends invitation email, creates pending membership | REQ-BT-005 |
| UC-005 | Team Admin | `/roles create clinician` | Creates new role definition in YAML config | REQ-BT-005 |
| UC-006 | Developer | `/api version create v2` | Creates versioned API namespace with routes | REQ-BT-001 |
| UC-007 | Ops | `/billing usage` | Returns current token/API usage summary | REQ-BT-001 |
| UC-008 | Developer | `/action create DischargePatient --target=Admission` | Generates action model scaffold | REQ-BT-001 |
| UC-009 | Developer | `/webhook create https://ehr.local/hook --events=patient.created,patient.updated` | Registers webhook endpoint with event filter | REQ-BT-010 |
| UC-010 | Compliance | `/audit log --user=dr.smith@hospital.org --since=7d` | Returns audit entries for user in last 7 days | REQ-BT-009 |
| UC-011 | Developer | `/registry discover triage` | Queries Global Agent Registry for agents with triage capability | REQ-BT-006 |
| UC-012 | Developer | `/a2a send triage-agent '{"patient_id":"P001"}'` | Sends A2A message to triage agent, returns task ID | REQ-BT-007 |
| UC-013 | Developer | `/fhir validate Patient.json` | Validates FHIR R4 resource, reports errors | REQ-BT-008 |

## Part B — Global Agent Registry

| UC-ID | Actor | Action | Expected Outcome | Traces To |
|-------|-------|--------|------------------|-----------|
| UC-GAR-001 | Agent Operator | Register agent via manifest POST | Agent visible in registry with capabilities indexed | REQ-GAR-001, REQ-GAR-002 |
| UC-GAR-002 | Developer | Discover agents by capability "triage" | Returns list of agents with triage capability, scoped by jurisdiction | REQ-GAR-004, REQ-GAR-006 |
| UC-GAR-003 | System | Verify trust for incoming agent request | Runs deny->hook->allow->escalate flow; returns permission decision | REQ-GAR-007 |
| UC-GAR-004 | Emergency Clinician | Break-glass access to agent outside normal trust | Access granted, audit entry created, alert sent | REQ-GAR-009 |
| UC-GAR-005 | Sovereign Admin | Override Root trust policy for national jurisdiction | Sovereign policy takes precedence within its scope | REQ-GAR-010, REQ-GAR-011 |
| UC-GAR-006 | Org Admin | Attempt to weaken Sovereign deny rule | System rejects the weakening, deny rule preserved | REQ-GAR-012 |

## Part C — Nexus A2A Protocol

| UC-ID | Actor | Action | Expected Outcome | Traces To |
|-------|-------|--------|------------------|-----------|
| UC-N2A-001 | Agent A | Send task to Agent B | Task accepted, 13-point admission passes, execution begins | REQ-N2A-001 to REQ-N2A-003 |
| UC-N2A-002 | Triage Agent | Receive ED intake payload | Agent subprocess spawned, FHIR payload piped via stdin, result via stdout | REQ-N2A-010 to REQ-N2A-012 |
| UC-N2A-003 | System | Long-running task with checkpoints | Task cycles Accept->Checkpoint->Checkpoint->Complete with JSONL persistence | REQ-N2A-006, REQ-N2A-014 |
| UC-N2A-004 | System | Task with patient data | Provider forced to Bevan (on-prem) regardless of agent config | REQ-N2A-018, REQ-N2A-019 |
| UC-N2A-005 | System | Conversation exceeds token threshold | Auto-compaction triggers, preserving recent context | REQ-N2A-008 |
| UC-N2A-006 | Auditor | Review clinical conversation chain | Session fork lineage traceable from current to root | REQ-N2A-015 |
| UC-N2A-007 | System | Admission check 9 (jurisdiction) fails | Route rejected with specific error code for point 9 | REQ-N2A-001, REQ-N2A-003 |
| UC-N2A-008 | System | Primary LLM provider down | Failover to secondary provider, task continues | REQ-N2A-020 |
