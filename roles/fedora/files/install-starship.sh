#!/bin/bash
# Verify release bytes before extraction; receipts track version and installed content.
set -euo pipefail
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
version=${RELEASE_VERSION:-v1.24.2}
checksum=${RELEASE_SHA256:-00ff3c1f8ffb59b5c15d4b44c076bcca04d92cf0055c86b916248c14f3ae714a}
url=${RELEASE_URL:-https://github.com/starship/starship/releases/download/v1.24.2/starship-x86_64-unknown-linux-musl.tar.gz}
manifest="$HOME/.local/state/nervhq/starship.sha256"
receipt="$manifest.release"
if [ -f "$receipt" ] && [ "$(cat "$receipt")" = "$version $checksum" ] &&
   shasum -a 256 -c "$manifest" >/dev/null 2>&1; then
  exit 0
fi
curl --fail --silent --show-error --location "$url" -o "$work_dir/archive"
printf '%s  %s\n' "$checksum" "$work_dir/archive" | shasum -a 256 -c -
tar -xzf "$work_dir/archive" -C "$work_dir"
mkdir -p "$HOME/.local/bin"
install -m 755 "$work_dir/starship" "$HOME/.local/bin/starship"
mkdir -p "$(dirname "$manifest")"
shasum -a 256 "$HOME/.local/bin/starship" > "$manifest.tmp"
mv "$manifest.tmp" "$manifest"
printf '%s %s\n' "$version" "$checksum" > "$receipt.tmp"
mv "$receipt.tmp" "$receipt"
echo NERVHQ_CHANGED
