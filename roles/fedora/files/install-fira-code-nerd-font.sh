#!/bin/bash

# Install Fira Code Nerd Font
# Based on: https://www.nerdfonts.com/font-downloads

set -euo pipefail

# Create font directory if it doesn't exist
mkdir -p "$HOME/.local/share/fonts"

# Download the latest Fira Code Nerd Font
curl -L -o /tmp/FiraCode.zip https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip

# Extract to fonts directory
unzip -o /tmp/FiraCode.zip -d "$HOME/.local/share/fonts/" "*.ttf"

# Update font cache
fc-cache -fv

# Clean up
rm /tmp/FiraCode.zip