#!/bin/bash
# Release archives are pinned and verified before extraction. No remote installer is executed.
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
curl --fail --silent --show-error --location "https://github.com/volta-cli/volta/releases/download/v2.0.2/volta-2.0.2-$platform.tar.gz" -o "$work_dir/archive"
printf '%s  %s\n' "$checksum" "$work_dir/archive" | shasum -a 256 -c -
tar -xzf "$work_dir/archive" -C "$work_dir"
mkdir -p "$HOME/.volta/bin"
# Install the primary binary last: the Ansible creates marker means installation completed.
for binary in volta-shim volta-migrate volta; do
  install -m 755 "$work_dir/$binary" "$HOME/.volta/bin/$binary"
done
