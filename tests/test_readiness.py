"""Runtime checks use temporary homes and fake downloads, never the workstation."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTALLERS = list(ROOT.glob('roles/*/files/*.sh'))


class Readiness(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.env = dict(os.environ, ANSIBLE_REMOTE_TEMP=temporary.name)

    def test_successful_http_with_corrupt_archive_is_rejected(self):
        for script in INSTALLERS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                home = root / 'home'
                home.mkdir()
                bin_dir = root / 'bin'
                bin_dir.mkdir()
                curl = bin_dir / 'curl'
                curl.write_text('#!/bin/bash\nwhile [ "$#" -gt 0 ]; do\n'
                                'if [ "$1" = -o ]; then shift; out=$1; fi\n'
                                'shift\ndone\nprintf corrupt > "$out"\n')
                curl.chmod(0o755)
                env = dict(os.environ, HOME=str(home), TMPDIR=tmp,
                           PATH=str(bin_dir) + ':' + os.environ['PATH'])
                result = subprocess.run(['bash', str(script)], env=env,
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(home.iterdir()), [])
                self.assertEqual(sorted(p.name for p in root.iterdir()), ['bin', 'home'])

    def test_inventory_loads_catalogs(self):
        result = subprocess.run(['ansible-inventory', '--host', 'localhost'],
                                cwd=ROOT, env=self.env, check=True, capture_output=True, text=True)
        host = json.loads(result.stdout)
        for name in ['applications', 'cli_tools', 'fonts']:
            self.assertGreater(len(host[name]), 0)
        self.assertEqual(host['ansible_connection'], 'local')

    def test_catalog_sources_and_script_markers(self):
        catalogs = [yaml.safe_load(p.read_text()) for p in
                    (ROOT / 'inventory/group_vars/all').glob('*.yml')]
        for catalog in catalogs:
            for items in catalog.values():
                if not isinstance(items, list):
                    continue
                for item in items:
                    for platform in ['arch', 'fedora', 'macos']:
                        config = item.get(platform, {})
                        if config.get('source') == 'script':
                            self.assertTrue((ROOT / 'roles' / platform / 'files' /
                                             config['script_name']).is_file())
                            self.assertTrue(config.get('creates'))
                        if config.get('source') in ['pacman', 'paru', 'dnf']:
                            self.assertNotIn('.', config.get('name', item['name']))

    def test_user_environment_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            playbook = Path(tmp) / 'test.yml'
            playbook.write_text(yaml.safe_dump([{
                'name': 'Isolated user environment test',
                'hosts': 'localhost', 'gather_facts': False,
                'vars': {'ansible_facts': {'env': {'HOME': tmp}}},
                'tasks': [{'name': 'Configure path', 'ansible.builtin.import_tasks':
                           str(ROOT / 'tasks/user_environment.yml')}],
            }]))
            for expected in ['changed=1', 'changed=0']:
                result = subprocess.run(['ansible-playbook', str(playbook)], cwd=ROOT, env=self.env,
                                        capture_output=True, text=True, check=True)
                self.assertIn(expected, result.stdout)
            contents = (Path(tmp) / '.zshrc').read_text()
            self.assertEqual(contents.count('export VOLTA_HOME='), 1)

    def test_aur_block_cleans_up_on_success_and_failure(self):
        # Exercise the real block/always orchestration with harmless file-backed
        # resource tasks. This does not claim to exercise useradd, sudo, or Paru.
        tasks = yaml.safe_load((ROOT / 'roles/arch/tasks/main.yml').read_text())
        block = next(task for task in tasks if 'block' in task)
        for fail in [False, True]:
            with self.subTest(fail=fail), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                marker = root / 'builder-resource'
                names = ['create_aur_builder_user', 'upgrade_packages', 'install_cli_tools',
                         'install_applications', 'install_fonts', 'configure_default_shell',
                         'remove_aur_builder_user']
                for name in names:
                    if name == 'create_aur_builder_user':
                        task = {'name': 'Create simulated resource', 'ansible.builtin.file':
                                {'path': str(marker), 'state': 'touch', 'mode': '0600'}}
                    elif name == 'remove_aur_builder_user':
                        task = {'name': 'Remove simulated resource', 'ansible.builtin.file':
                                {'path': str(marker), 'state': 'absent'}}
                    elif name == 'install_cli_tools' and fail:
                        task = {'name': 'Fail simulated package install',
                                'ansible.builtin.fail': {'msg': 'Deliberate package failure'}}
                    else:
                        task = {'name': 'Simulate successful step',
                                'ansible.builtin.debug': {'msg': name}}
                    (root / (name + '.yml')).write_text(yaml.safe_dump([task]))
                play = [{'name': 'Isolated AUR orchestration', 'hosts': 'localhost',
                         'gather_facts': False,
                         'vars': {'workstation_upgrade_packages': True}, 'tasks': [block]}]
                path = root / 'test.yml'
                path.write_text(yaml.safe_dump(play))
                result = subprocess.run(['ansible-playbook', str(path)], cwd=ROOT,
                                        env=self.env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2 if fail else 0, result.stdout + result.stderr)
                self.assertFalse(marker.exists(), result.stdout)
                self.assertIn('Remove simulated resource', result.stdout)

    def test_wrong_os_fails_before_mutation(self):
        # Independent of the CI operating system: deliberately request another family.
        target = 'local-macos.yml' if os.uname().sysname != 'Darwin' else 'local-fedora.yml'
        result = subprocess.run(['ansible-playbook', target], cwd=ROOT, env=self.env,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('changed=0', result.stdout)
        self.assertIn('Run as your desktop user with Python 3.14', result.stdout)


if __name__ == '__main__':
    unittest.main()
