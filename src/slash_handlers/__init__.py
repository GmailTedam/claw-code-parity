from __future__ import annotations

from ..slash_commands import ParsedSlashCommand, SlashCommandResult
from .bullettrain import handle_bullettrain_command
from .healthcare import handle_healthcare_command

BULLETTRAIN_COMMANDS = frozenset([
    'scaffold', 'scaffold:api', 'scaffold:join', 'team', 'roles',
    'api', 'billing', 'action', 'webhook', 'audit', 'theme', 'db',
])

HEALTHCARE_COMMANDS = frozenset(['registry', 'a2a', 'fhir'])


def dispatch_slash_command(parsed: ParsedSlashCommand) -> SlashCommandResult | None:
    if parsed.name in BULLETTRAIN_COMMANDS:
        return handle_bullettrain_command(parsed)
    if parsed.name in HEALTHCARE_COMMANDS:
        return handle_healthcare_command(parsed)
    return None
