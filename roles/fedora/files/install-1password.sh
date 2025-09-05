#!/bin/bash

# Install 1Password on Fedora/RHEL
# Based on: https://support.1password.com/install-linux/#fedora-or-red-hat-enterprise-linux

set -euo pipefail

# Import the 1Password GPG key
rpm --import https://downloads.1password.com/linux/keys/1password.asc

# Add the 1Password yum repository
cat > /etc/yum.repos.d/1password.repo << 'EOF'
[1password]
name=1Password Stable Channel
baseurl=https://downloads.1password.com/linux/rpm/stable/$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey="https://downloads.1password.com/linux/keys/1password.asc"
EOF

# Install 1Password
dnf install -y 1password
