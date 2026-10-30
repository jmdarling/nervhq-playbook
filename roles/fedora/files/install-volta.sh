#!/bin/bash

# Install Volta Node.js version manager from the official installer.
set -euo pipefail

installer=$(mktemp)
trap 'rm -f "$installer"' EXIT
curl --fail --silent --show-error --location https://get.volta.sh -o "$installer"
bash "$installer"
