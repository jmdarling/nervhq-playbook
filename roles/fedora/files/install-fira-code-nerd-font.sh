#!/bin/bash
# Verify release bytes before extraction; receipts track version and installed content.
set -euo pipefail
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
version=${RELEASE_VERSION:-v3.4.0}
checksum=${RELEASE_SHA256:-7cc4ffd8f7a1fc914cdab7b149808298165ff7a7f40e40d82dea9ebe41e8ca0b}
url=${RELEASE_URL:-https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/FiraCode.zip}
manifest="$HOME/.local/state/nervhq/font.sha256"
receipt="$manifest.release"
if [ -f "$receipt" ] && [ "$(cat "$receipt")" = "$version $checksum" ] &&
   shasum -a 256 -c "$manifest" >/dev/null 2>&1; then
  exit 0
fi
curl --fail --silent --show-error --location "$url" -o "$work_dir/archive"
printf '%s  %s\n' "$checksum" "$work_dir/archive" | shasum -a 256 -c -
unzip -q "$work_dir/archive" '*.ttf' -d "$work_dir/fonts"
mkdir -p "$HOME/.local/share/fonts"
install -m 644 "$work_dir/fonts/"*.ttf "$HOME/.local/share/fonts/"
fc-cache -f "$HOME/.local/share/fonts"

mkdir -p "$(dirname "$manifest")"
shasum -a 256 "$HOME/.local/share/fonts/"FiraCode*.ttf > "$manifest.tmp"
mv "$manifest.tmp" "$manifest"
printf '%s %s\n' "$version" "$checksum" > "$receipt.tmp"
mv "$receipt.tmp" "$receipt"
echo NERVHQ_CHANGED
