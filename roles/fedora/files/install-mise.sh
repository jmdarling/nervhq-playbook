#!/bin/bash
# Verify release bytes before extraction; receipts track version and installed content.
set -euo pipefail
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
version=${RELEASE_VERSION:-v2026.10.25}
checksum=${RELEASE_SHA256:-199966edaad1b208eb4c72955f1722dafb8fa799f575db720dea05aaa8216546}
url=${RELEASE_URL:-https://github.com/jdx/mise/releases/download/v2026.10.25/mise-v2026.10.25-linux-x64.tar.gz}
manifest="$HOME/.local/state/nervhq/mise.sha256"
receipt="$manifest.release"
if [ -f "$receipt" ] && [ "$(cat "$receipt")" = "$version $checksum" ] &&
   sha256sum -c "$manifest" >/dev/null 2>&1; then
  exit 0
fi
curl --fail --silent --show-error --location "$url" -o "$work_dir/archive"
printf '%s  %s\n' "$checksum" "$work_dir/archive" | sha256sum -c -
tar -xzf "$work_dir/archive" -C "$work_dir"
mkdir -p "$HOME/.local/bin"
install -m 755 "$work_dir/mise/bin/mise" "$HOME/.local/bin/mise"
mkdir -p "$(dirname "$manifest")"
sha256sum "$HOME/.local/bin/mise" > "$manifest.tmp"
mv "$manifest.tmp" "$manifest"
printf '%s %s\n' "$version" "$checksum" > "$receipt.tmp"
mv "$receipt.tmp" "$receipt"
echo NERVHQ_CHANGED
