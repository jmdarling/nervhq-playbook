#!/bin/bash
# Verify release bytes before extraction; receipts track version and installed content.
set -euo pipefail
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    platform=linux
    checksum=6cec054c911fb925b629a09455775af6e95dc0f5694a4c28b63979ab9ef18037 ;;
  Darwin-arm64)
    platform=macos
    checksum=57f7b51d6fb975f5c48b5ddf68f75103055e19fd822e3e2ce58d2be6ab78977d ;;
  *) echo 'Unsupported Volta platform' >&2; exit 1 ;;
esac
version=${RELEASE_VERSION:-v2.0.2}
checksum=${RELEASE_SHA256:-$checksum}
url=${RELEASE_URL:-https://github.com/volta-cli/volta/releases/download/v2.0.2/volta-2.0.2-$platform.tar.gz}
manifest="$HOME/.local/state/nervhq/volta.sha256"
receipt="$manifest.release"
if [ -f "$receipt" ] && [ "$(cat "$receipt")" = "$version $checksum" ] &&
   shasum -a 256 -c "$manifest" >/dev/null 2>&1; then
  exit 0
fi
curl --fail --silent --show-error --location "$url" -o "$work_dir/archive"
printf '%s  %s\n' "$checksum" "$work_dir/archive" | shasum -a 256 -c -
tar -xzf "$work_dir/archive" -C "$work_dir"
mkdir -p "$HOME/.volta/bin"
# Write the release receipt only after all binaries install successfully.
for binary in volta-shim volta-migrate volta; do
  install -m 755 "$work_dir/$binary" "$HOME/.volta/bin/$binary"
done
mkdir -p "$(dirname "$manifest")"
shasum -a 256 "$HOME/.volta/bin/volta" "$HOME/.volta/bin/volta-shim" "$HOME/.volta/bin/volta-migrate" > "$manifest.tmp"
mv "$manifest.tmp" "$manifest"
printf '%s %s\n' "$version" "$checksum" > "$receipt.tmp"
mv "$receipt.tmp" "$receipt"
echo NERVHQ_CHANGED
