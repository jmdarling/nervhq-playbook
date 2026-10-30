#!/bin/bash
# Release archives are pinned and verified before extraction. No remote installer is executed.
set -euo pipefail
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
curl --fail --silent --show-error --location https://github.com/starship/starship/releases/download/v1.24.2/starship-x86_64-unknown-linux-musl.tar.gz -o "$work_dir/archive"
printf '%s  %s\n' 00ff3c1f8ffb59b5c15d4b44c076bcca04d92cf0055c86b916248c14f3ae714a "$work_dir/archive" | shasum -a 256 -c -
tar -xzf "$work_dir/archive" -C "$work_dir"
mkdir -p "$HOME/.local/bin"
install -m 755 "$work_dir/starship" "$HOME/.local/bin/starship"
