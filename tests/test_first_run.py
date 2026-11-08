"""Exercise first-run setup without touching the test host's packages or users."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class FirstRun(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.env = dict(os.environ, HOME=temporary.name,
                        ANSIBLE_LOCAL_TEMP=str(self.root / 'local-tmp'),
                        ANSIBLE_REMOTE_TEMP=str(self.root / 'remote-tmp'),
                        ANSIBLE_COLLECTIONS_PATH=str(self.root / 'collections'),
                        ANSIBLE_COLLECTIONS_SCAN_SYS_PATH='false')

    def run_play(self, tasks, variables=None, extra_args=()):
        play = self.root / 'test.yml'
        play.write_text(yaml.safe_dump([{
            'name': 'Isolated first-run test', 'hosts': 'localhost',
            'gather_facts': False, 'vars': variables or {}, 'tasks': tasks,
        }]))
        return subprocess.run(['ansible-playbook', str(play), *extra_args],
                              cwd=ROOT, env=self.env, text=True, capture_output=True)

    def test_preflight_does_not_reject_version_numbers(self):
        for fedora, python in [('39', 12), ('44', 14), ('45', 15), ('99', 20)]:
            with self.subTest(fedora=fedora, python=python):
                result = self.run_play([{'name': 'Validate target',
                    'ansible.builtin.import_tasks': str(ROOT / 'tasks/preflight.yml')}], {
                    'workstation_os': 'fedora', 'applications': [], 'cli_tools': [], 'fonts': [],
                    'ansible_facts': {
                        'python': {'version': {'major': 3, 'minor': python}},
                        'user_uid': 1000, 'env': {'HOME': str(self.root)},
                        'distribution': 'Fedora', 'distribution_major_version': fedora,
                        'architecture': 'x86_64',
                    },
                })
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('changed=0', result.stdout)

    def build_fixture_collection(self):
        source = self.root / 'collection-source'
        (source / 'plugins/modules').mkdir(parents=True)
        (source / 'README.md').write_text('Offline test fixture, not a real collection.\n')
        (source / 'galaxy.yml').write_text(yaml.safe_dump({
            'namespace': 'community', 'name': 'general', 'version': '1.0.0',
            'readme': 'README.md', 'authors': ['Test fixture'],
        }))
        (source / 'plugins/modules/bootstrap_probe.py').write_text(
            'from ansible.module_utils.basic import AnsibleModule\n'
            'AnsibleModule(argument_spec={}).exit_json(changed=False, msg="collection-loaded")\n')
        result = subprocess.run(['ansible-galaxy', 'collection', 'build',
                                 '--output-path', str(self.root)],
                                cwd=source, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_installed_collection_is_reused_without_changes(self):
        self.build_fixture_collection()
        result = subprocess.run(['ansible-galaxy', 'collection', 'install', '--no-deps',
                                 str(self.root / 'community-general-1.0.0.tar.gz')],
                                cwd=ROOT, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        role_tasks = self.root / 'collection-tasks.yml'
        role_tasks.write_text(yaml.safe_dump([{
            'name': 'Load newly installed collection', 'community.general.bootstrap_probe': {},
        }]))
        tasks = [
            {'name': 'Prepare controller',
             'ansible.builtin.import_tasks': str(ROOT / 'tasks/controller.yml')},
            {'name': 'Load dynamic tasks', 'ansible.builtin.include_tasks': str(role_tasks)},
        ]
        for changes in [0, 0]:
            result = self.run_play(tasks)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Load newly installed collection', result.stdout)
            self.assertIn(f'changed={changes}', result.stdout)

    def test_core_only_has_actionable_failure_before_role_loading(self):
        result = self.run_play([{'name': 'Prepare controller',
            'ansible.builtin.import_tasks': str(ROOT / 'tasks/controller.yml')}])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sudo dnf install ansible', result.stdout + result.stderr)
        self.assertIn('changed=0', result.stdout)

    def test_missing_bindings_bootstrap_for_both_dnf_backends_and_converge(self):
        for backend, package in [('dnf', 'python3-dnf'), ('dnf5', 'python3-libdnf5')]:
            with self.subTest(backend=backend):
                marker = self.root / (backend + '-installed')
                arguments = self.root / (backend + '-arguments')
                python = self.root / (backend + '-python')
                python.write_text(f'#!/bin/sh\ntest -f "{marker}"\n')
                python.chmod(0o755)
                dnf = self.root / (backend + '-command')
                dnf.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{arguments}"\n'
                               f'touch "{marker}"\n')
                dnf.chmod(0o755)
                tasks = yaml.safe_load((ROOT / 'roles/fedora/tasks/bootstrap.yml').read_text())[:2]
                # Substitute harmless fixture commands; retain the real argument
                # selection, result conditions and changed reporting from the role.
                tasks[0]['ansible.builtin.command']['argv'][0] = str(python)
                tasks[1]['ansible.builtin.command']['argv'][0] = str(dnf)
                tasks[1]['become'] = False
                for changes in [1, 0]:
                    result = self.run_play(tasks, {'ansible_facts': {'pkg_mgr': backend}})
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(f'changed={changes}', result.stdout)
                self.assertEqual(arguments.read_text().splitlines(), ['install', '-y', package])

    def test_clean_smoke_uses_distro_ansible_and_no_development_bootstrap(self):
        smoke = (ROOT / 'tests/fedora-smoke.sh').read_text()
        self.assertIn('dnf5 install -y ansible sudo', smoke)
        self.assertNotIn('PYTHON=python3 bash scripts/bootstrap.sh', smoke)
        self.assertNotIn('export PATH="$PWD/.venv/bin:$PATH"', smoke)
        catalogs = yaml.safe_load((ROOT / 'inventory/group_vars/all/cli_tools.yml').read_text())
        git = next(tool for tool in catalogs['cli_tools'] if tool['name'] == 'git')
        self.assertEqual(git['fedora']['source'], 'dnf')
        bootstrap = (ROOT / 'roles/fedora/tasks/bootstrap.yml').read_text()
        self.assertIn('gzip', bootstrap)
        self.assertNotIn('dnf5-plugins', bootstrap)
        self.assertNotIn('perl-Digest-SHA', bootstrap)


if __name__ == '__main__':
    unittest.main()
