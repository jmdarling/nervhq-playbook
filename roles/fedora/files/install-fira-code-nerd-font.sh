#!/bin/bash

# Install Fira Code Nerd Font
# Based on: https://www.nerdfonts.com/font-downloads

set -euo pipefail

# Create font directory if it doesn't exist
mkdir -p "$HOME/.local/share/fonts"

archive=$(mktemp)
trap 'rm -f "$archive"' EXIT

# Download the latest Fira Code Nerd Font
curl --fail --silent --show-error --location -o "$archive" https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip

# Extract to fonts directory
unzip -o "$archive" -d "$HOME/.local/share/fonts/" "*.ttf"

# Update font cache
fc-cache -fv
