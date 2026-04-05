from __future__ import annotations

import re

from ..slash_commands import FIELD_TYPE_PATTERN, URL_PATTERN, ParsedSlashCommand, SlashCommandResult


def handle_bullettrain_command(parsed: ParsedSlashCommand) -> SlashCommandResult:
    handler = _HANDLERS.get(parsed.name)
    if handler is None:
        return SlashCommandResult(command=parsed.name, handled=False, message=f'Unknown BulletTrain command: /{parsed.name}')
    return handler(parsed)


def _handle_scaffold(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args:
        return SlashCommandResult(command='scaffold', handled=False, message='Usage: /scaffold <Model> [field:type...]')
    parts = parsed.raw_args.split()
    model_name = parts[0]
    if not model_name[0].isupper():
        return SlashCommandResult(command='scaffold', handled=False, message=f"Model name '{model_name}' must start with an uppercase letter")
    fields = parts[1:]
    for field_spec in fields:
        if not FIELD_TYPE_PATTERN.match(field_spec):
            return SlashCommandResult(command='scaffold', handled=False, message=f"Invalid field syntax '{field_spec}' — expected name:type (e.g. name:string)")
    field_summary = ', '.join(fields) if fields else 'no fields'
    return SlashCommandResult(
        command='scaffold',
        handled=True,
        message=f'Scaffold {model_name} with {len(fields)} fields ({field_summary}): model, controller, views, API endpoint, and tests generated.',
    )


def _handle_scaffold_api(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args:
        return SlashCommandResult(command='scaffold:api', handled=False, message='Usage: /scaffold:api <Model> [field:type...]')
    parts = parsed.raw_args.split()
    model_name = parts[0]
    if not model_name[0].isupper():
        return SlashCommandResult(command='scaffold:api', handled=False, message=f"Model name '{model_name}' must start with an uppercase letter")
    fields = parts[1:]
    for field_spec in fields:
        if not FIELD_TYPE_PATTERN.match(field_spec):
            return SlashCommandResult(command='scaffold:api', handled=False, message=f"Invalid field syntax '{field_spec}' — expected name:type")
    return SlashCommandResult(
        command='scaffold:api',
        handled=True,
        message=f'API-only scaffold {model_name} with {len(fields)} fields: model, serializer, and API endpoint generated (no views).',
    )


def _handle_scaffold_join(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args:
        return SlashCommandResult(command='scaffold:join', handled=False, message='Usage: /scaffold:join <ModelA> <ModelB>')
    parts = parsed.raw_args.split()
    if len(parts) < 2:
        return SlashCommandResult(command='scaffold:join', handled=False, message='Usage: /scaffold:join <ModelA> <ModelB> — two model names required')
    model_a, model_b = parts[0], parts[1]
    join_name = f'{model_a}{model_b}'
    return SlashCommandResult(
        command='scaffold:join',
        handled=True,
        message=f'Join model {join_name} generated with belongs_to :{model_a.lower()} and belongs_to :{model_b.lower()}.',
    )


def _handle_team(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None or action == 'list':
        return SlashCommandResult(command='team', handled=True, message='Team members: (list would be rendered here)')
    if action == 'invite':
        if not parsed.target:
            return SlashCommandResult(command='team', handled=False, message='Usage: /team invite <email>')
        return SlashCommandResult(command='team', handled=True, message=f'Invitation sent to {parsed.target}.')
    if action == 'remove':
        if not parsed.target:
            return SlashCommandResult(command='team', handled=False, message='Usage: /team remove <email>')
        return SlashCommandResult(command='team', handled=True, message=f'Member {parsed.target} removed from team.')
    if action == 'switch':
        if not parsed.target:
            return SlashCommandResult(command='team', handled=False, message='Usage: /team switch <name>')
        return SlashCommandResult(command='team', handled=True, message=f'Switched to team: {parsed.target}')
    return SlashCommandResult(command='team', handled=False, message=f"Unknown /team action '{action}'. Use list, invite, remove, or switch.")


def _handle_roles(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None or action == 'list':
        return SlashCommandResult(command='roles', handled=True, message='Role definitions: (list would be rendered here)')
    if action == 'create':
        if not parsed.target:
            return SlashCommandResult(command='roles', handled=False, message='Usage: /roles create <name>')
        return SlashCommandResult(command='roles', handled=True, message=f'Role {parsed.target} created.')
    if action == 'assign':
        if not parsed.target:
            return SlashCommandResult(command='roles', handled=False, message='Usage: /roles assign <role> <user>')
        return SlashCommandResult(command='roles', handled=True, message=f'Role assignment: {parsed.target}')
    return SlashCommandResult(command='roles', handled=False, message=f"Unknown /roles action '{action}'. Use list, create, or assign.")


def _handle_api(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args:
        return SlashCommandResult(command='api', handled=True, message='API status: (summary would be rendered here)')
    args = parsed.raw_args
    if args.startswith('version create'):
        version = args.replace('version create', '').strip()
        if not version:
            return SlashCommandResult(command='api', handled=False, message='Usage: /api version create <version>')
        return SlashCommandResult(command='api', handled=True, message=f'API version {version} created with versioned namespace and routes.')
    if args.startswith('endpoints'):
        return SlashCommandResult(command='api', handled=True, message='API endpoints: (route list would be rendered here)')
    if args.startswith('token'):
        return SlashCommandResult(command='api', handled=True, message='API token generated.')
    return SlashCommandResult(command='api', handled=False, message=f'Unknown /api subcommand. Use version create, endpoints list, or token generate.')


def _handle_billing(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None or action == 'usage':
        return SlashCommandResult(command='billing', handled=True, message='Billing usage: (usage summary would be rendered here)')
    if action == 'plans':
        return SlashCommandResult(command='billing', handled=True, message='Available plans: (plan list would be rendered here)')
    if action == 'subscribe':
        if not parsed.target:
            return SlashCommandResult(command='billing', handled=False, message='Usage: /billing subscribe <plan>')
        return SlashCommandResult(command='billing', handled=True, message=f'Subscribed to plan: {parsed.target}')
    return SlashCommandResult(command='billing', handled=False, message=f"Unknown /billing action '{action}'. Use plans list, subscribe, or usage.")


def _handle_action(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args:
        return SlashCommandResult(command='action', handled=True, message='Action models: (list would be rendered here)')
    args = parsed.raw_args
    if args.startswith('create'):
        remainder = args[len('create'):].strip()
        if not remainder:
            return SlashCommandResult(command='action', handled=False, message='Usage: /action create <Name> [--target=<Model>]')
        parts = remainder.split()
        name = parts[0]
        target = None
        for part in parts[1:]:
            if part.startswith('--target='):
                target = part.split('=', 1)[1]
        msg = f'Action model {name} created'
        if target:
            msg += f' targeting {target}'
        return SlashCommandResult(command='action', handled=True, message=f'{msg}.')
    if args.startswith('trigger'):
        name = args[len('trigger'):].strip()
        if not name:
            return SlashCommandResult(command='action', handled=False, message='Usage: /action trigger <Name>')
        return SlashCommandResult(command='action', handled=True, message=f'Action {name} triggered.')
    if args.startswith('list'):
        return SlashCommandResult(command='action', handled=True, message='Action models: (list would be rendered here)')
    return SlashCommandResult(command='action', handled=False, message='Unknown /action subcommand. Use create, trigger, or list.')


def _handle_webhook(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None or action == 'list':
        return SlashCommandResult(command='webhook', handled=True, message='Webhooks: (list would be rendered here)')
    if action == 'create':
        if not parsed.target:
            return SlashCommandResult(command='webhook', handled=False, message='Usage: /webhook create <url>')
        url = parsed.target.split()[0]
        if not URL_PATTERN.match(url):
            return SlashCommandResult(command='webhook', handled=False, message=f"Invalid URL '{url}' — must start with http:// or https://")
        return SlashCommandResult(command='webhook', handled=True, message=f'Webhook registered: {url}')
    if action == 'test':
        if not parsed.target:
            return SlashCommandResult(command='webhook', handled=False, message='Usage: /webhook test <id>')
        return SlashCommandResult(command='webhook', handled=True, message=f'Test payload sent to webhook {parsed.target}.')
    if action == 'delete':
        if not parsed.target:
            return SlashCommandResult(command='webhook', handled=False, message='Usage: /webhook delete <id>')
        return SlashCommandResult(command='webhook', handled=True, message=f'Webhook {parsed.target} deleted.')
    return SlashCommandResult(command='webhook', handled=False, message=f"Unknown /webhook action '{action}'. Use create, test, list, or delete.")


def _handle_audit(parsed: ParsedSlashCommand) -> SlashCommandResult:
    if not parsed.raw_args or parsed.raw_args == 'log':
        return SlashCommandResult(command='audit', handled=True, message='Audit log: (recent entries would be rendered here)')
    args = parsed.raw_args
    user_filter = None
    since_filter = None
    for token in args.split():
        if token.startswith('--user='):
            user_filter = token.split('=', 1)[1]
        elif token.startswith('--since='):
            since_filter = token.split('=', 1)[1]
    filters = []
    if user_filter:
        filters.append(f'user={user_filter}')
    if since_filter:
        filters.append(f'since={since_filter}')
    filter_summary = ', '.join(filters) if filters else 'no filters'
    return SlashCommandResult(command='audit', handled=True, message=f'Audit log ({filter_summary}): (filtered entries would be rendered here)')


def _handle_theme(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None or action == 'list':
        return SlashCommandResult(command='theme', handled=True, message='Themes: (available themes would be rendered here)')
    if action == 'set':
        if not parsed.target:
            return SlashCommandResult(command='theme', handled=False, message='Usage: /theme set <name>')
        return SlashCommandResult(command='theme', handled=True, message=f'Theme set to: {parsed.target}')
    if action == 'customize':
        return SlashCommandResult(command='theme', handled=True, message='Theme customization: (editor would open here)')
    return SlashCommandResult(command='theme', handled=False, message=f"Unknown /theme action '{action}'. Use set, list, or customize.")


def _handle_db(parsed: ParsedSlashCommand) -> SlashCommandResult:
    action = parsed.action
    if action is None:
        return SlashCommandResult(command='db', handled=True, message='Database status: (summary would be rendered here)')
    if action == 'seed':
        return SlashCommandResult(command='db', handled=True, message='Database seeded successfully.')
    if action == 'reset':
        return SlashCommandResult(command='db', handled=True, message='Database reset successfully.')
    if action == 'migrate':
        return SlashCommandResult(command='db', handled=True, message='Database migrations applied successfully.')
    return SlashCommandResult(command='db', handled=False, message=f"Unknown /db action '{action}'. Use seed, reset, or migrate.")


_HANDLERS: dict[str, object] = {
    'scaffold': _handle_scaffold,
    'scaffold:api': _handle_scaffold_api,
    'scaffold:join': _handle_scaffold_join,
    'team': _handle_team,
    'roles': _handle_roles,
    'api': _handle_api,
    'billing': _handle_billing,
    'action': _handle_action,
    'webhook': _handle_webhook,
    'audit': _handle_audit,
    'theme': _handle_theme,
    'db': _handle_db,
}
