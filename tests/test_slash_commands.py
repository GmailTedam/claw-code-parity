from __future__ import annotations

import subprocess
import sys
import unittest

from src.slash_commands import (
    CommandSource,
    bullettrain_specs,
    feature_gated_specs,
    get_spec,
    healthcare_specs,
    parse_slash_command,
    render_help,
    render_slash_command_index,
    resume_supported_specs,
    slash_command_specs,
)
from src.slash_handlers import dispatch_slash_command


class SlashCommandSpecTests(unittest.TestCase):
    def test_total_spec_count(self) -> None:
        self.assertEqual(len(slash_command_specs()), 41)

    def test_resume_supported_count(self) -> None:
        self.assertEqual(len(resume_supported_specs()), 16)

    def test_bullettrain_spec_count(self) -> None:
        self.assertEqual(len(bullettrain_specs()), 12)

    def test_healthcare_spec_count(self) -> None:
        self.assertEqual(len(healthcare_specs()), 3)

    def test_feature_gated_spec_count(self) -> None:
        specs = feature_gated_specs()
        self.assertEqual(len(specs), 3)
        names = {spec.name for spec in specs}
        self.assertEqual(names, {'registry', 'a2a', 'fhir'})

    def test_all_specs_have_name_and_summary(self) -> None:
        for spec in slash_command_specs():
            self.assertTrue(spec.name, f'Spec missing name: {spec}')
            self.assertTrue(spec.summary, f'Spec {spec.name} missing summary')

    def test_command_names_follow_pattern(self) -> None:
        import re
        pattern = re.compile(r'^[a-z][a-z0-9:_-]*$')
        for spec in slash_command_specs():
            self.assertRegex(spec.name, pattern, f'Spec name invalid: {spec.name}')

    def test_get_spec_by_name(self) -> None:
        spec = get_spec('scaffold')
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, 'scaffold')

    def test_get_spec_by_alias(self) -> None:
        spec = get_spec('webhooks')
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, 'webhook')

        spec = get_spec('database')
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, 'db')

        spec = get_spec('plugins')
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, 'plugin')

    def test_get_spec_unknown(self) -> None:
        self.assertIsNone(get_spec('nonexistent'))


class SlashCommandParserTests(unittest.TestCase):
    def test_parse_simple_command(self) -> None:
        parsed = parse_slash_command('/help')
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, 'help')
        self.assertIsNone(parsed.action)

    def test_parse_command_with_action(self) -> None:
        parsed = parse_slash_command('/team invite')
        self.assertEqual(parsed.name, 'team')
        self.assertEqual(parsed.action, 'invite')

    def test_parse_command_with_action_and_target(self) -> None:
        parsed = parse_slash_command('/team invite doctor@hospital.org')
        self.assertEqual(parsed.name, 'team')
        self.assertEqual(parsed.action, 'invite')
        self.assertEqual(parsed.target, 'doctor@hospital.org')

    def test_parse_alias_resolves(self) -> None:
        parsed = parse_slash_command('/webhooks list')
        self.assertEqual(parsed.name, 'webhook')
        parsed = parse_slash_command('/database seed')
        self.assertEqual(parsed.name, 'db')

    def test_parse_scaffold_with_fields(self) -> None:
        parsed = parse_slash_command('/scaffold Patient name:string dob:date')
        self.assertEqual(parsed.name, 'scaffold')
        self.assertEqual(parsed.raw_args, 'Patient name:string dob:date')

    def test_parse_colon_command(self) -> None:
        parsed = parse_slash_command('/scaffold:api Appointment')
        self.assertEqual(parsed.name, 'scaffold:api')
        self.assertEqual(parsed.raw_args, 'Appointment')

    def test_parse_non_slash_returns_none(self) -> None:
        self.assertIsNone(parse_slash_command('not a command'))

    def test_parse_empty_returns_none(self) -> None:
        self.assertIsNone(parse_slash_command(''))


class ScaffoldHandlerTests(unittest.TestCase):
    def test_scaffold_with_valid_fields(self) -> None:
        parsed = parse_slash_command('/scaffold Patient name:string dob:date mrn:string')
        result = dispatch_slash_command(parsed)
        self.assertTrue(result.handled)
        self.assertIn('Patient', result.message)
        self.assertIn('3 fields', result.message)

    def test_scaffold_missing_model(self) -> None:
        parsed = parse_slash_command('/scaffold')
        result = dispatch_slash_command(parsed)
        self.assertFalse(result.handled)
        self.assertIn('Usage', result.message)

    def test_scaffold_invalid_field_syntax(self) -> None:
        parsed = parse_slash_command('/scaffold Patient bad_field')
        result = dispatch_slash_command(parsed)
        self.assertFalse(result.handled)
        self.assertIn('Invalid field syntax', result.message)

    def test_scaffold_lowercase_model_rejected(self) -> None:
        parsed = parse_slash_command('/scaffold patient')
        result = dispatch_slash_command(parsed)
        self.assertFalse(result.handled)
        self.assertIn('uppercase', result.message)

    def test_scaffold_api(self) -> None:
        parsed = parse_slash_command('/scaffold:api Appointment')
        result = dispatch_slash_command(parsed)
        self.assertTrue(result.handled)
        self.assertIn('API-only', result.message)

    def test_scaffold_join(self) -> None:
        parsed = parse_slash_command('/scaffold:join Patient Provider')
        result = dispatch_slash_command(parsed)
        self.assertTrue(result.handled)
        self.assertIn('PatientProvider', result.message)
        self.assertIn('belongs_to', result.message)

    def test_scaffold_join_needs_two_models(self) -> None:
        parsed = parse_slash_command('/scaffold:join Patient')
        result = dispatch_slash_command(parsed)
        self.assertFalse(result.handled)
        self.assertIn('two model names', result.message)


class TeamRolesHandlerTests(unittest.TestCase):
    def test_team_list(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/team list'))
        self.assertTrue(result.handled)

    def test_team_invite(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/team invite doctor@hospital.org'))
        self.assertTrue(result.handled)
        self.assertIn('doctor@hospital.org', result.message)

    def test_team_invite_missing_email(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/team invite'))
        self.assertFalse(result.handled)
        self.assertIn('Usage', result.message)

    def test_team_switch(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/team switch cardiology'))
        self.assertTrue(result.handled)
        self.assertIn('cardiology', result.message)

    def test_team_unknown_action(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/team explode'))
        self.assertFalse(result.handled)

    def test_roles_list(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/roles list'))
        self.assertTrue(result.handled)

    def test_roles_create(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/roles create clinician'))
        self.assertTrue(result.handled)
        self.assertIn('clinician', result.message)


class WebhookHandlerTests(unittest.TestCase):
    def test_webhook_create_valid_url(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/webhook create https://ehr.local/hook'))
        self.assertTrue(result.handled)
        self.assertIn('https://ehr.local/hook', result.message)

    def test_webhook_create_invalid_url(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/webhook create not-a-url'))
        self.assertFalse(result.handled)
        self.assertIn('Invalid URL', result.message)

    def test_webhook_list(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/webhook list'))
        self.assertTrue(result.handled)

    def test_webhook_alias(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/webhooks list'))
        self.assertTrue(result.handled)

    def test_webhook_test(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/webhook test hook-123'))
        self.assertTrue(result.handled)

    def test_webhook_delete(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/webhook delete hook-123'))
        self.assertTrue(result.handled)


class AuditHandlerTests(unittest.TestCase):
    def test_audit_log(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/audit log'))
        self.assertTrue(result.handled)

    def test_audit_with_filters(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/audit log --user=dr.smith@hospital.org --since=7d'))
        self.assertTrue(result.handled)
        self.assertIn('user=dr.smith@hospital.org', result.message)
        self.assertIn('since=7d', result.message)


class BillingApiActionDbThemeTests(unittest.TestCase):
    def test_billing_usage(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/billing usage'))
        self.assertTrue(result.handled)

    def test_billing_subscribe(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/billing subscribe pro'))
        self.assertTrue(result.handled)
        self.assertIn('pro', result.message)

    def test_api_version_create(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/api version create v2'))
        self.assertTrue(result.handled)
        self.assertIn('v2', result.message)

    def test_api_endpoints_list(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/api endpoints list'))
        self.assertTrue(result.handled)

    def test_action_create_with_target(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/action create DischargePatient --target=Admission'))
        self.assertTrue(result.handled)
        self.assertIn('DischargePatient', result.message)
        self.assertIn('Admission', result.message)

    def test_action_trigger(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/action trigger DischargePatient'))
        self.assertTrue(result.handled)

    def test_db_migrate(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/db migrate'))
        self.assertTrue(result.handled)
        self.assertIn('migrations', result.message)

    def test_db_alias(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/database seed'))
        self.assertTrue(result.handled)
        self.assertIn('seeded', result.message)

    def test_theme_set(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/theme set dark'))
        self.assertTrue(result.handled)
        self.assertIn('dark', result.message)


class HealthcareHandlerTests(unittest.TestCase):
    def test_registry_list(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/registry list'))
        self.assertTrue(result.handled)

    def test_registry_discover(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/registry discover triage'))
        self.assertTrue(result.handled)
        self.assertIn('triage', result.message)

    def test_registry_trust(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/registry trust agent-001'))
        self.assertTrue(result.handled)
        self.assertIn('agent-001', result.message)

    def test_a2a_agents(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/a2a agents'))
        self.assertTrue(result.handled)

    def test_a2a_send(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/a2a send triage-agent {"patient_id":"P001"}'))
        self.assertTrue(result.handled)
        self.assertIn('triage-agent', result.message)

    def test_a2a_status(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/a2a status task-123'))
        self.assertTrue(result.handled)
        self.assertIn('task-123', result.message)

    def test_fhir_validate(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/fhir validate Patient.json'))
        self.assertTrue(result.handled)
        self.assertIn('Patient.json', result.message)

    def test_fhir_transform(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/fhir transform Bundle.json'))
        self.assertTrue(result.handled)
        self.assertIn('Bundle.json', result.message)

    def test_fhir_search(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/fhir search Observation'))
        self.assertTrue(result.handled)
        self.assertIn('Observation', result.message)

    def test_fhir_no_args(self) -> None:
        result = dispatch_slash_command(parse_slash_command('/fhir'))
        self.assertFalse(result.handled)
        self.assertIn('Usage', result.message)


class CoreCommandDispatchTests(unittest.TestCase):
    def test_core_commands_return_none(self) -> None:
        for cmd in ['/help', '/status', '/compact', '/model', '/version']:
            parsed = parse_slash_command(cmd)
            result = dispatch_slash_command(parsed)
            self.assertIsNone(result, f'Core command {cmd} should return None from dispatch')


class RenderTests(unittest.TestCase):
    def test_render_help_contains_all_commands(self) -> None:
        help_text = render_help()
        self.assertIn('/scaffold', help_text)
        self.assertIn('/team', help_text)
        self.assertIn('/registry', help_text)
        self.assertIn('/a2a', help_text)
        self.assertIn('/fhir', help_text)
        self.assertIn('aliases: /webhooks', help_text)
        self.assertIn('aliases: /database', help_text)

    def test_render_index_all(self) -> None:
        index = render_slash_command_index()
        self.assertIn('All Slash Commands', index)
        self.assertIn('Total: 41', index)

    def test_render_index_bullettrain(self) -> None:
        index = render_slash_command_index('bullettrain')
        self.assertIn('BulletTrain', index)
        self.assertIn('Total: 12', index)

    def test_render_index_healthcare(self) -> None:
        index = render_slash_command_index('healthcare')
        self.assertIn('Healthcare', index)
        self.assertIn('Total: 3', index)


class CliIntegrationTests(unittest.TestCase):
    def test_slash_commands_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-commands'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('All Slash Commands', result.stdout)
        self.assertIn('Total: 41', result.stdout)

    def test_slash_commands_category_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-commands-category', 'bullettrain'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('BulletTrain', result.stdout)
        self.assertIn('Total: 12', result.stdout)

    def test_slash_help_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-help'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('Slash commands', result.stdout)
        self.assertIn('/scaffold', result.stdout)

    def test_slash_exec_scaffold_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-exec', '/scaffold Patient name:string'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('Patient', result.stdout)
        self.assertIn('1 fields', result.stdout)

    def test_slash_exec_webhook_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-exec', '/webhook create https://ehr.local/hook'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('https://ehr.local/hook', result.stdout)

    def test_slash_exec_core_command_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-exec', '/help'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('handled by runtime', result.stdout)

    def test_slash_exec_registry_discover_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', 'slash-exec', '/registry discover triage'],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('triage', result.stdout)


if __name__ == '__main__':
    unittest.main()
