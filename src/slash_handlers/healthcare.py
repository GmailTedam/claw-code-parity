from __future__ import annotations

from ..slash_commands import ParsedSlashCommand, SlashCommandResult


def handle_healthcare_command(parsed: ParsedSlashCommand) -> SlashCommandResult:
    handler = _HANDLERS.get(parsed.name)
    if handler is None:
        return SlashCommandResult(command=parsed.name, handled=False, message=f'Unknown healthcare command: /{parsed.name}')
    return handler(parsed)


def _handle_registry(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None or action == 'list':
        return SlashCommandResult(command='registry', handled=True, message='Agent Registry: (registered agents would be listed here)')
    if action == 'discover':
        if not parsed.target:
            return SlashCommandResult(command='registry', handled=False, message='Usage: /registry discover <capability>')
        return SlashCommandResult(
            command='registry',
            handled=True,
            message=f"Agent Registry discover: agents with capability '{parsed.target}' (results would be rendered here)",
        )
    if action == 'trust':
        if not parsed.target:
            return SlashCommandResult(command='registry', handled=False, message='Usage: /registry trust <agent-id>')
        return SlashCommandResult(command='registry', handled=True, message=f'Trust verification for agent {parsed.target}: (trust bundle would be rendered here)')
    return SlashCommandResult(command='registry', handled=False, message=f"Unknown /registry action '{action}'. Use list, discover, or trust.")


def _handle_a2a(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args or parsed.raw_args == 'agents':
        return SlashCommandResult(command='a2a', handled=True, message='A2A agents: (available agents would be listed here)')
    args = parsed.raw_args
    if args.startswith('send'):
        remainder = args[len('send'):].strip()
        if not remainder:
            return SlashCommandResult(command='a2a', handled=False, message='Usage: /a2a send <agent> <payload>')
        parts = remainder.split(None, 1)
        agent_name = parts[0]
        payload = parts[1] if len(parts) > 1 else '{}'
        return SlashCommandResult(
            command='a2a',
            handled=True,
            message=f'A2A task sent to {agent_name}: payload accepted, task_id generated (task status would be returned here)',
        )
    if args.startswith('status'):
        task_id = args[len('status'):].strip()
        if not task_id:
            return SlashCommandResult(command='a2a', handled=False, message='Usage: /a2a status <task-id>')
        return SlashCommandResult(command='a2a', handled=True, message=f'A2A task {task_id}: (task status would be rendered here)')
    return SlashCommandResult(command='a2a', handled=False, message='Unknown /a2a subcommand. Use send, status, or agents.')


def _handle_fhir(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args:
        return SlashCommandResult(command='fhir', handled=False, message='Usage: /fhir [validate <resource>|transform <bundle>|search <type>]')
    args = parsed.raw_args
    if args.startswith('validate'):
        resource = args[len('validate'):].strip()
        if not resource:
            return SlashCommandResult(command='fhir', handled=False, message='Usage: /fhir validate <resource>')
        return SlashCommandResult(command='fhir', handled=True, message=f'FHIR R4 validation for {resource}: (validation results would be rendered here)')
    if args.startswith('transform'):
        bundle = args[len('transform'):].strip()
        if not bundle:
            return SlashCommandResult(command='fhir', handled=False, message='Usage: /fhir transform <bundle>')
        return SlashCommandResult(command='fhir', handled=True, message=f'FHIR bundle {bundle} transformed: (transformation results would be rendered here)')
    if args.startswith('search'):
        resource_type = args[len('search'):].strip()
        if not resource_type:
            return SlashCommandResult(command='fhir', handled=False, message='Usage: /fhir search <type>')
        return SlashCommandResult(command='fhir', handled=True, message=f'FHIR search for {resource_type}: (search results would be rendered here)')
    return SlashCommandResult(command='fhir', handled=False, message='Unknown /fhir subcommand. Use validate, transform, or search.')


_HANDLERS: dict[str, object] = {
    'registry': _handle_registry,
    'a2a': _handle_a2a,
    'fhir': _handle_fhir,
}
