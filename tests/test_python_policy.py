"""Keep controller selection and update policy consistent across entry points."""
import json
from pathlib import Path
import tomllib
import unittest

from packaging.specifiers import SpecifierSet
import yaml

ROOT = Path(__file__).resolve().parents[1]


class PythonPolicy(unittest.TestCase):
    def test_runtime_and_renovate_accept_patches_but_reject_other_minors(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        runtime = SpecifierSet(project['project']['requires-python'])
        rules = json.loads((ROOT / 'renovate.json').read_text())['packageRules']
        rule = next(rule for rule in rules if rule.get('matchDepNames') == ['python'])
        self.assertEqual(rule['matchManagers'], ['github-actions'])
        allowed = SpecifierSet(','.join(rule['allowedVersions'].split()))
        for version, expected in [('3.14.0', True), ('3.14.99', True),
                                  ('3.13.9', False), ('3.15.0', False)]:
            self.assertEqual(version in runtime, expected)
            self.assertEqual(version in allowed, expected)
        workflow = yaml.safe_load((ROOT / '.github/workflows/validate.yml').read_text())
        selected = [step['with']['python-version'] for job in workflow['jobs'].values()
                    for step in job['steps'] if step.get('uses', '').startswith('actions/setup-python@')]
        self.assertEqual(selected, ['3.14'])
        bootstrap = (ROOT / 'scripts/bootstrap.sh').read_text()
        self.assertIn('PYTHON:-python3.14', bootstrap)
        self.assertIn('sys.version_info[:2] == (3, 14)', bootstrap)
        preflight = (ROOT / 'tasks/preflight.yml').read_text()
        self.assertIn('ansible_facts.python.version.minor == 14', preflight)
        inventory = yaml.safe_load((ROOT / 'inventory/hosts.yml').read_text())
        self.assertEqual(inventory['all']['hosts']['localhost']['ansible_python_interpreter'],
                         '{{ ansible_playbook_python }}')
