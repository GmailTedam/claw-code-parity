from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache


class CommandSource(Enum):
    BUILTIN = 'builtin'
    FEATURE_GATED = 'feature_gated'
    INTERNAL_ONLY = 'internal_only'


@dataclass(frozen=True)
class SlashCommandSpec:
    name: str
    aliases: tuple[str, ...] = ()
    summary: str = ''
    argument_hint: str | None = None
    resume_supported: bool = False
    source: CommandSource = CommandSource.BUILTIN


@dataclass(frozen=True)
class SlashCommandResult:
    command: str
    handled: bool
    message: str


@dataclass(frozen=True)
class ParsedSlashCommand:
    name: str
    action: str | None = None
    target: str | None = None
    raw_args: str | None = None


SLASH_COMMAND_SPECS: tuple[SlashCommandSpec, ...] = (
    # --- Core CLI commands (mirrored from Rust) ---
    SlashCommandSpec(name='help', summary='Show available slash commands', resume_supported=True),
    SlashCommandSpec(name='status', summary='Show current session status', resume_supported=True),
    SlashCommandSpec(name='sandbox', summary='Show sandbox isolation status', resume_supported=True),
    SlashCommandSpec(name='compact', summary='Compact local session history', resume_supported=True),
    SlashCommandSpec(name='model', summary='Show or switch the active model', argument_hint='[model]'),
    SlashCommandSpec(name='permissions', summary='Show or switch the active permission mode', argument_hint='[read-only|workspace-write|danger-full-access]'),
    SlashCommandSpec(name='clear', summary='Start a fresh local session', argument_hint='[--confirm]', resume_supported=True),
    SlashCommandSpec(name='cost', summary='Show cumulative token usage for this session', resume_supported=True),
    SlashCommandSpec(name='resume', summary='Load a saved session into the REPL', argument_hint='<session-path>'),
    SlashCommandSpec(name='config', summary='Inspect Claude config files or merged sections', argument_hint='[env|hooks|model|plugins]', resume_supported=True),
    SlashCommandSpec(name='memory', summary='Inspect loaded Claude instruction memory files', resume_supported=True),
    SlashCommandSpec(name='init', summary='Create a starter CLAUDE.md for this repo', resume_supported=True),
    SlashCommandSpec(name='diff', summary='Show git diff for current workspace changes', resume_supported=True),
    SlashCommandSpec(name='version', summary='Show CLI version and build information', resume_supported=True),
    SlashCommandSpec(name='bughunter', summary='Inspect the codebase for likely bugs', argument_hint='[scope]'),
    SlashCommandSpec(name='commit', summary='Generate a commit message and create a git commit'),
    SlashCommandSpec(name='pr', summary='Draft or create a pull request from the conversation', argument_hint='[context]'),
    SlashCommandSpec(name='issue', summary='Draft or create a GitHub issue from the conversation', argument_hint='[context]'),
    SlashCommandSpec(name='ultraplan', summary='Run a deep planning prompt with multi-step reasoning', argument_hint='[task]'),
    SlashCommandSpec(name='teleport', summary='Jump to a file or symbol by searching the workspace', argument_hint='<symbol-or-path>'),
    SlashCommandSpec(name='debug-tool-call', summary='Replay the last tool call with debug details'),
    SlashCommandSpec(name='export', summary='Export the current conversation to a file', argument_hint='[file]', resume_supported=True),
    SlashCommandSpec(name='session', summary='List, switch, or fork managed local sessions', argument_hint='[list|switch <session-id>|fork [branch-name]]'),
    SlashCommandSpec(name='plugin', aliases=('plugins', 'marketplace'), summary='Manage Claw Code plugins', argument_hint='[list|install <path>|enable <name>|disable <name>|uninstall <id>|update <id>]'),
    SlashCommandSpec(name='agents', summary='List configured agents', resume_supported=True),
    SlashCommandSpec(name='skills', summary='List available skills', resume_supported=True),
    # --- BulletTrain SaaS commands ---
    SlashCommandSpec(name='scaffold', summary='Generate model scaffolding with fields', argument_hint='<Model> [field:type...]', source=CommandSource.BUILTIN),
    SlashCommandSpec(name='scaffold:api', summary='Generate API-only scaffold', argument_hint='<Model> [field:type...]', source=CommandSource.BUILTIN),
    SlashCommandSpec(name='scaffold:join', summary='Generate join model between two models', argument_hint='<ModelA> <ModelB>', source=CommandSource.BUILTIN),
    SlashCommandSpec(name='team', summary='Manage team members and invitations', argument_hint='[invite <email>|remove <email>|list|switch <name>]'),
    SlashCommandSpec(name='roles', summary='Manage role definitions', argument_hint='[list|create <name>|assign <role> <user>]'),
    SlashCommandSpec(name='api', summary='Manage API versions and endpoints', argument_hint='[version create <v>|endpoints list|token generate]'),
    SlashCommandSpec(name='billing', summary='Manage billing plans and subscriptions', argument_hint='[plans list|subscribe <plan>|usage]'),
    SlashCommandSpec(name='action', summary='Manage action models', argument_hint='[create <Name> --target=<Model>|trigger <Name>|list]'),
    SlashCommandSpec(name='webhook', aliases=('webhooks',), summary='Manage webhooks and integrations', argument_hint='[create <url>|test <id>|list|delete <id>]'),
    SlashCommandSpec(name='audit', summary='Query audit logs', argument_hint='[log --user=<email> --since=<duration>]', resume_supported=True),
    SlashCommandSpec(name='theme', summary='Manage UI themes', argument_hint='[set <name>|list|customize]'),
    SlashCommandSpec(name='db', aliases=('database',), summary='Database operations', argument_hint='[seed|reset|migrate]'),
    # --- Healthcare bridge commands ---
    SlashCommandSpec(name='registry', summary='Query the agent registry', argument_hint='[list|discover <capability>|trust <agent-id>]', resume_supported=True, source=CommandSource.FEATURE_GATED),
    SlashCommandSpec(name='a2a', summary='Agent-to-agent operations', argument_hint='[send <agent> <payload>|status <task-id>|agents]', source=CommandSource.FEATURE_GATED),
    SlashCommandSpec(name='fhir', summary='FHIR resource operations', argument_hint='[validate <resource>|transform <bundle>|search <type>]', source=CommandSource.FEATURE_GATED),
)

FIELD_TYPE_PATTERN = re.compile(r'^[a-zA-Z_]\w*:[a-zA-Z_]\w*$')
URL_PATTERN = re.compile(r'^https?://')


@lru_cache(maxsize=1)
def slash_command_specs() -> tuple[SlashCommandSpec, ...]:
    return SLASH_COMMAND_SPECS


@lru_cache(maxsize=1)
def _alias_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for spec in SLASH_COMMAND_SPECS:
        for alias in spec.aliases:
            mapping[alias] = spec.name
    return mapping


def resume_supported_specs() -> tuple[SlashCommandSpec, ...]:
    return tuple(spec for spec in SLASH_COMMAND_SPECS if spec.resume_supported)


def feature_gated_specs() -> tuple[SlashCommandSpec, ...]:
    return tuple(spec for spec in SLASH_COMMAND_SPECS if spec.source == CommandSource.FEATURE_GATED)


def bullettrain_specs() -> tuple[SlashCommandSpec, ...]:
    bt_names = frozenset([
        'scaffold', 'scaffold:api', 'scaffold:join', 'team', 'roles',
        'api', 'billing', 'action', 'webhook', 'audit', 'theme', 'db',
    ])
    return tuple(spec for spec in SLASH_COMMAND_SPECS if spec.name in bt_names)


def healthcare_specs() -> tuple[SlashCommandSpec, ...]:
    hc_names = frozenset(['registry', 'a2a', 'fhir'])
    return tuple(spec for spec in SLASH_COMMAND_SPECS if spec.name in hc_names)


def get_spec(name: str) -> SlashCommandSpec | None:
    lowered = name.lower()
    canonical = _alias_map().get(lowered, lowered)
    for spec in SLASH_COMMAND_SPECS:
        if spec.name == canonical:
            return spec
    return None


def parse_slash_command(input_text: str) -> ParsedSlashCommand | None:
    trimmed = input_text.strip()
    if not trimmed.startswith('/'):
        return None
    without_slash = trimmed[1:]
    parts = without_slash.split(None, 2)
    if not parts:
        return None
    raw_name = parts[0]
    canonical = _alias_map().get(raw_name, raw_name)
    action = parts[1] if len(parts) > 1 else None
    target = parts[2] if len(parts) > 2 else None
    raw_args = without_slash[len(raw_name):].strip() or None
    return ParsedSlashCommand(name=canonical, action=action, target=target, raw_args=raw_args)


def render_help() -> str:
    lines = [
        'Slash commands',
        '  [resume] means the command also works with --resume SESSION.jsonl',
    ]
    for spec in SLASH_COMMAND_SPECS:
        name_display = f'/{spec.name}'
        if spec.argument_hint:
            name_display = f'{name_display} {spec.argument_hint}'
        alias_suffix = ''
        if spec.aliases:
            alias_suffix = f' (aliases: {", ".join(f"/{a}" for a in spec.aliases)})'
        resume = ' [resume]' if spec.resume_supported else ''
        lines.append(f'  {name_display:<44} {spec.summary}{alias_suffix}{resume}')
    return '\n'.join(lines)


def render_slash_command_index(category: str | None = None) -> str:
    if category == 'bullettrain':
        specs = bullettrain_specs()
        title = 'BulletTrain SaaS Commands'
    elif category == 'healthcare':
        specs = healthcare_specs()
        title = 'Healthcare Bridge Commands'
    elif category == 'feature-gated':
        specs = feature_gated_specs()
        title = 'Feature-Gated Commands'
    else:
        specs = SLASH_COMMAND_SPECS
        title = 'All Slash Commands'
    lines = [f'# {title}', '', f'Total: {len(specs)}', '']
    lines.extend(f'- /{spec.name} — {spec.summary}' for spec in specs)
    return '\n'.join(lines)
