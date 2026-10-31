"""Exercise actual installers with inert local archive fixtures, never upstream code."""
import hashlib
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class ReleaseUpgrades(unittest.TestCase):
    def test_versions_repairs_and_integrity_failure(self):
        for script in ROOT.glob('roles/*/files/*.sh'):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                home = root / 'home'
                home.mkdir()
                commands = root / 'commands'
                commands.mkdir()
                (commands / 'curl').write_text(
                    '#!/bin/bash\nwhile [ "$#" -gt 0 ]; do\n'
                    'if [ "$1" = -o ]; then shift; out=$1; fi\nshift\ndone\n'
                    'cp "$FIXTURE" "$out"\n')
                (commands / 'fc-cache').write_text('#!/bin/bash\nexit 0\n')
                for command in commands.iterdir():
                    command.chmod(0o755)
                env = dict(os.environ, HOME=str(home), TMPDIR=tmp,
                           PATH=str(commands) + ':' + os.environ['PATH'])
                if 'volta' in script.name:
                    files = ['volta', 'volta-shim', 'volta-migrate']
                    installed = home / '.volta/bin/volta'
                elif 'starship' in script.name:
                    files = ['starship']
                    installed = home / '.local/bin/starship'
                else:
                    files = ['FiraCodeNerdFont-Regular.ttf']
                    installed = home / '.local/share/fonts' / files[0]
                archive = root / 'fixture'

                def build(version):
                    payload = ('inert fixture ' + version).encode()
                    if 'font' in script.name:
                        with zipfile.ZipFile(archive, 'w') as output:
                            for name in files:
                                output.writestr(name, payload)
                    else:
                        with tarfile.open(archive, 'w:gz') as output:
                            for name in files:
                                member = tarfile.TarInfo(name)
                                member.size = len(payload)
                                output.addfile(member, io.BytesIO(payload))
                    env.update(FIXTURE=str(archive), RELEASE_VERSION=version,
                               RELEASE_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                               RELEASE_URL='https://example.invalid/fixture')
                    return payload

                def run(changed):
                    result = subprocess.run(['bash', str(script)], env=env,
                                            capture_output=True, text=True, check=True)
                    self.assertEqual('NERVHQ_CHANGED' in result.stdout, changed)

                first = build('v8.0.0')
                run(True)
                run(False)
                self.assertEqual(installed.read_bytes(), first)
                second = build('v8.1.0')
                run(True)
                run(False)
                self.assertEqual(installed.read_bytes(), second)
                installed.write_bytes(b'damaged')
                run(True)
                self.assertEqual(installed.read_bytes(), second)
                installed.unlink()
                run(True)
                # A failed new release must leave working files and receipt untouched.
                receipts = {p: p.read_bytes() for p in (home / '.local/state/nervhq').iterdir()}
                build('v8.2.0')
                archive.write_bytes(b'corrupt')
                result = subprocess.run(['bash', str(script)], env=env,
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(installed.read_bytes(), second)
                self.assertEqual(receipts, {p: p.read_bytes() for p in receipts})
                self.assertEqual(sorted(p.name for p in root.iterdir()),
                                 ['commands', 'fixture', 'home'])
