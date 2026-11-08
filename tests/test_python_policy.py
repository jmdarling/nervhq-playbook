"""Keep optional development tooling separate from the workstation runtime."""
import json
from pathlib import Path
import tomllib
import unittest

from packaging.specifiers import SpecifierSet
import yaml

ROOT = Path(__file__).resolve().parents[1]


class PythonPolicy(unittest.TestCase):
    def test_no_arbitrary_python_or_workstation_version_allowlist(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        development_python = SpecifierSet(project['project']['requires-python'])
        # This minimum is required by pinned ansible-core, not by the playbook.
        self.assertEqual(str(development_python), '>=3.13')
        for version in ['3.13.0', '3.14.0', '3.15.0', '3.16.0']:
            self.assertIn(version, development_python)
        renovate = json.loads((ROOT / 'renovate.json').read_text())
        self.assertFalse(any('python' in rule.get('matchDepNames', [])
                             and 'allowedVersions' in rule
                             for rule in renovate.get('packageRules', [])))
        workflow = yaml.safe_load((ROOT / '.github/workflows/validate.yml').read_text())
        self.assertEqual(workflow['jobs']['static-checks']['strategy']['matrix']['python'],
                         ['3.13', '3.14', '3.15'])
        bootstrap = (ROOT / 'scripts/bootstrap.sh').read_text()
        self.assertIn('PYTHON:-python3', bootstrap)
        self.assertNotIn('sys.version_info', bootstrap)
        preflight = (ROOT / 'tasks/preflight.yml').read_text()
        self.assertNotIn('ansible_facts.python.version', preflight)
        self.assertNotIn('ansible_version', preflight)
        self.assertNotIn('distribution_major_version', preflight)
        inventory = yaml.safe_load((ROOT / 'inventory/hosts.yml').read_text())
        self.assertEqual(inventory['all']['hosts']['localhost']['ansible_python_interpreter'],
                         '{{ ansible_playbook_python }}')
