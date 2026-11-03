#!/bin/bash
# Preserve other global tools/settings while managing the floating Node LTS request.
set -euo pipefail
mise=$1
cd "$HOME"
config=${MISE_GLOBAL_CONFIG_FILE:-${XDG_CONFIG_HOME:-$HOME/.config}/mise/config.toml}
shims=${MISE_DATA_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/mise}/shims
# Bootstrap and trust only the user's global file, never project configurations.
mkdir -p "$(dirname "$config")"
if [ ! -f "$config" ]; then touch "$config"; fi
"$mise" trust "$config"

snapshot() {
  if [ -f "$config" ]; then cat "$config"; fi
  "$mise" ls --installed --json node
  for binary in node npm npx; do
    if [ -L "$shims/$binary" ]; then
      readlink "$shims/$binary"
    else
      printf 'missing shim: %s\n' "$binary"
    fi
  done
}

before=$(snapshot)
"$mise" config set --global tools.node lts
# Reuse an installed LTS when upgrades are disabled; still provision missing Node.
if [ "${NERVHQ_UPGRADE_NODE:-true}" = true ] || ! "$mise" where node@lts >/dev/null 2>&1; then
  "$mise" install node@lts
fi
"$mise" reshim
after=$(snapshot)
if [ "$before" != "$after" ]; then echo NERVHQ_CHANGED; fi
