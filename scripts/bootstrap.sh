#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_command=${PYTHON:-python3.14}
"$python_command" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 14) else "Python 3.14 is required; Python 3.15 is incompatible with the pinned Ansible tooling.")'
"$python_command" -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml
