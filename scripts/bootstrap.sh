#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_command=${PYTHON:-python3}
"$python_command" -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
