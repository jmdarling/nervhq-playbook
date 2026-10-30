#!/bin/bash

# Install Starship from the official installer.
set -euo pipefail

installer=$(mktemp)
trap 'rm -f "$installer"' EXIT
curl --fail --silent --show-error --location https://starship.rs/install.sh -o "$installer"
sh "$installer" -y
