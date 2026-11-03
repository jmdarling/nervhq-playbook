"""Inert mise stand-in for isolated Ansible and shell integration checks."""
import json
import os
from pathlib import Path
import re
import sys

home = Path.home()
config = home / '.config/mise/config.toml'
data = home / '.local/share/mise'
installed = data / 'installed'
args = sys.argv[1:]
with (home / 'mise-calls').open('a') as calls:
    calls.write(' '.join(args) + '\n')

if args[0] == 'trust':
    assert args[1] == str(config)
elif args == ['ls', '--installed', '--json', 'node']:
    print(json.dumps([{'version': installed.read_text()}] if installed.exists() else []))
elif args == ['config', 'set', '--global', 'tools.node', 'lts']:
    contents = config.read_text() if config.exists() else ''
    if '[tools]\n' not in contents:
        contents += '[tools]\n'
    if re.search(r'^node\s*=', contents, re.M):
        contents = re.sub(r'^node\s*=.*$', 'node = "lts"', contents, flags=re.M)
    else:
        contents = contents.replace('[tools]\n', '[tools]\nnode = "lts"\n')
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(contents)
elif args == ['where', 'node@lts']:
    if not installed.exists():
        sys.exit(1)
    print(data / 'bin')
elif args[0] == 'install':
    if os.environ.get('NERVHQ_TEST_INSTALL_FAIL'):
        sys.exit(42)
    if args[1] == 'node@lts' or not installed.exists():
        data.mkdir(parents=True, exist_ok=True)
        installed.write_text(os.environ.get('NERVHQ_TEST_LTS', '24.0.0'))
elif args == ['reshim']:
    (data / 'bin').mkdir(parents=True, exist_ok=True)
    (data / 'shims').mkdir(exist_ok=True)
    for name in ['node', 'npm', 'npx']:
        binary = data / 'bin' / name
        binary.write_text('#!/bin/sh\necho fixture-' + name + '\n')
        binary.chmod(0o755)
        shim = data / 'shims' / name
        if not shim.is_symlink():
            shim.symlink_to(binary)
elif args[:2] == ['activate', 'zsh']:
    print('export PATH="$HOME/.local/share/mise/shims:$PATH"')
else:
    raise SystemExit('Unexpected fake mise arguments: ' + repr(args))
