#!/bin/bash

# Install Volta Node.js version manager
# Based on: https://volta.sh/

set -euo pipefail

# Download and run the Volta installer
curl -sS https://starship.rs/install.sh | sh -s -- -y
