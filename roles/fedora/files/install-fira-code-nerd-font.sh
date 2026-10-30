#!/bin/bash
# Release archives are pinned and verified before extraction. No remote installer is executed.
set -euo pipefail
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
curl --fail --silent --show-error --location https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/FiraCode.zip -o "$work_dir/archive"
printf '%s  %s\n' 7cc4ffd8f7a1fc914cdab7b149808298165ff7a7f40e40d82dea9ebe41e8ca0b "$work_dir/archive" | shasum -a 256 -c -
unzip -q "$work_dir/archive" '*.ttf' -d "$work_dir/fonts"
mkdir -p "$HOME/.local/share/fonts"
install -m 644 "$work_dir/fonts/"*.ttf "$HOME/.local/share/fonts/"
fc-cache -f "$HOME/.local/share/fonts"
touch "$HOME/.local/share/fonts/.nervhq-firacode-3.4.0"
