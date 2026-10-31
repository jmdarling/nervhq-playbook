"""Exercise verifier orchestration with fake tools; never execute downloaded code."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
FINGERPRINT = '3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4'


class ChatGPTBootstrap(unittest.TestCase):
    def test_verification_order_and_rejections(self):
        for failure in ['', 'sha256sum', 'gpg-import', 'fingerprint', 'rpmkeys', 'identity']:
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                work = root / 'work'
                work.mkdir()
                commands = root / 'bin'
                commands.mkdir()
                fake = f'''#!{sys.executable}
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ['CALLS'], 'a') as log:
    log.write(json.dumps([name, args]) + '\\n')
failure = os.environ['FAILURE']
if name == failure:
    sys.exit(1)
if name == 'gpg':
    if '--import' in args and failure == 'gpg-import':
        sys.exit(1)
    if '--fingerprint' in args:
        print('fpr:::::::::' + ('WRONG' if failure == 'fingerprint' else '{FINGERPRINT}') + ':')
    if '--export' in args:
        print('inert armored-key fixture')
if name == 'rpm' and '-qp' in args:
    print('wrong-package' if failure == 'identity' else 'chatgpt 26.1027.30824-1 x86_64', end='')
'''
                for command in ['sha256sum', 'gpg', 'rpm', 'rpmkeys']:
                    path = commands / command
                    path.write_text(fake)
                    path.chmod(0o755)
                calls_file = root / 'calls'
                env = dict(os.environ, FAILURE=failure, CALLS=str(calls_file),
                           PATH=str(commands) + ':' + os.environ['PATH'])
                result = subprocess.run(['bash', str(ROOT / 'scripts/verify-chatgpt-rpm.sh'), str(work)],
                                        env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode == 0, failure == '', result.stderr)
                calls = [json.loads(line) for line in calls_file.read_text().splitlines()]
                names = [name for name, _ in calls]
                self.assertEqual(names[0], 'sha256sum')
                if failure in ['sha256sum', 'gpg-import', 'fingerprint']:
                    self.assertNotIn('rpm', names)
                    self.assertNotIn('rpmkeys', names)
                if failure == 'rpmkeys':
                    self.assertFalse(any('-qp' in args for _, args in calls))
                for name, args in calls:
                    if name in ['rpm', 'rpmkeys']:
                        self.assertEqual(args[:2], ['--dbpath', str(work / 'rpmdb')])
                        self.assertNotIn('-i', args)
                if not failure:
                    self.assertLess(names.index('rpmkeys'), len(names) - 1)
                    self.assertEqual(calls[-1][0], 'rpm')

    def test_privileged_install_follows_verification_and_cleanup_is_unconditional(self):
        tasks = yaml.safe_load((ROOT / 'roles/fedora/tasks/bootstrap_chatgpt_payload.yml').read_text())
        block = tasks[1]['block']
        verification = next(i for i, task in enumerate(block) if 'ansible.builtin.script' in task)
        self.assertTrue(all(not task.get('become', False) for task in block[:verification + 1]))
        self.assertTrue(all(task.get('become', False) for task in block[verification + 1:]))
        install = block[-1]['ansible.builtin.dnf5']
        self.assertFalse(install['disable_gpg_check'])
        self.assertFalse(install['allow_downgrade'])
        self.assertEqual(tasks[1]['always'][0]['ansible.builtin.file']['state'], 'absent')
        for task in block[:verification]:
            self.assertTrue(task['ansible.builtin.get_url']['checksum'].startswith('sha256:'))
