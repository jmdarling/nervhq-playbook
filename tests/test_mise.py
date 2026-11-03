"""Check runtime provisioning, migration, opt-out and fresh Zsh integration safely."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class MiseEnvironment(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        (self.home / 'roles').symlink_to(ROOT / 'roles', target_is_directory=True)
        self.mise = self.home / '.local/bin/mise'
        self.mise.parent.mkdir(parents=True)
        self.mise.write_text('#!' + sys.executable + '\n' +
                             (ROOT / 'tests/fixtures/mise.py').read_text())
        self.mise.chmod(0o755)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(('MISE_', 'XDG_'))}
        self.env.update(HOME=str(self.home), ANSIBLE_HOME=str(self.home / '.ansible'),
                        ANSIBLE_REMOTE_TEMP=str(self.home / '.ansible/tmp'))
        self.config = self.home / '.config/mise/config.toml'
        self.config.parent.mkdir(parents=True)
        self.config.write_text('[tools]\nnode = "22"\npnpm = "10"\n'
                               '[settings]\nexperimental = false\n')
        # Preserve unrelated user content while replacing the old managed Volta block.
        (self.home / '.zshrc').write_text(
            'export NERVHQ_TEST_USER_SETTING=preserved\n'
            '# BEGIN NERVHQ USER TOOLS\nexport VOLTA_HOME="$HOME/.volta"\n'
            'export PATH="$VOLTA_HOME/bin:$PATH"\n# END NERVHQ USER TOOLS\n')
        (self.home / '.zprofile').write_text('export NERVHQ_TEST_PROFILE=preserved\n')
        self.playbook = self.home / 'test.yml'

    def run_playbook(self, expected, enabled=True, upgrades=True):
        self.playbook.write_text(yaml.safe_dump([{
            'name': 'Isolated mise environment test', 'hosts': 'localhost',
            'gather_facts': False,
            'vars': {'ansible_facts': {'env': {'HOME': str(self.home)}},
                     'workstation_os': 'fedora', 'workstation_upgrade_packages': upgrades,
                     'cli_tools': [{'name': 'mise', 'fedora': {'source': 'script'}}] if enabled else []},
            'tasks': [{'name': 'Configure environment', 'ansible.builtin.import_tasks':
                       str(ROOT / 'tasks/user_environment.yml')}],
        }]))
        result = subprocess.run(['ansible-playbook', str(self.playbook)], cwd=ROOT,
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('changed=' + str(expected), result.stdout)

    def test_global_lts_migration_repeat_run_upgrade_and_shim_repair(self):
        self.run_playbook(3)
        self.assertIn('node = "lts"', self.config.read_text())
        self.assertIn('pnpm = "10"', self.config.read_text())
        self.assertIn('experimental = false', self.config.read_text())
        self.assertNotIn('VOLTA_HOME', (self.home / '.zshrc').read_text())
        self.assertIn('NERVHQ_TEST_USER_SETTING=preserved', (self.home / '.zshrc').read_text())
        self.assertIn('NERVHQ_TEST_PROFILE=preserved', (self.home / '.zprofile').read_text())
        self.run_playbook(0)
        self.env['NERVHQ_TEST_LTS'] = '26.0.0'
        self.run_playbook(0, upgrades=False)
        self.run_playbook(1)
        shims = self.home / '.local/share/mise/shims'
        (shims / 'npm').unlink()
        self.run_playbook(1)
        self.assertTrue((shims / 'npm').is_symlink())
        self.run_playbook(0)

    def test_missing_runtime_installs_when_upgrades_disabled(self):
        self.run_playbook(3, upgrades=False)
        self.assertIn('install node@lts\n', (self.home / 'mise-calls').read_text())
        self.run_playbook(0, upgrades=False)

    def test_first_run_creates_global_configuration(self):
        self.config.unlink()
        self.run_playbook(3)
        self.assertIn('node = "lts"', self.config.read_text())
        self.run_playbook(0)

    def test_omitting_mise_skips_runtime_and_activation(self):
        self.run_playbook(2, enabled=False)
        self.assertFalse((self.home / 'mise-calls').exists())
        self.assertIn('node = "22"', self.config.read_text())
        for name in ['.zshrc', '.zprofile']:
            self.assertNotIn('activate zsh', (self.home / name).read_text())
        self.run_playbook(0, enabled=False)

    @unittest.skipUnless(shutil.which('zsh'), 'Zsh runtime checks also run in the Fedora smoke test')
    def test_fresh_interactive_and_login_shells(self):
        self.run_playbook(3)
        env = dict(self.env, PATH='/usr/bin:/bin', ZDOTDIR=str(self.home))
        for mode in ['-ic', '-lc', '-lic']:
            result = subprocess.run([shutil.which('zsh'), mode,
                                     'node --version && npm --version && npx --version'],
                                    env=env, cwd=self.home, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('fixture-node', result.stdout)
            self.assertIn('fixture-npm', result.stdout)
        calls = (self.home / 'mise-calls').read_text()
        self.assertIn('activate zsh\n', calls)
        self.assertIn('activate zsh --shims\n', calls)

    def test_runtime_install_failure_is_reported(self):
        self.env['NERVHQ_TEST_INSTALL_FAIL'] = '1'
        result = subprocess.run(['bash', str(ROOT / 'roles/common/files/configure-mise.sh'),
                                 str(self.mise)], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 42)
        self.assertNotIn('NERVHQ_CHANGED', result.stdout)
        self.assertNotIn('reshim\n', (self.home / 'mise-calls').read_text())
