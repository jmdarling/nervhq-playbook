#!/bin/bash

# Install Visual Studio Code on Fedora/RHEL
# Based on: https://code.visualstudio.com/docs/setup/linux#_rhel-fedora-and-centos-based-distributions

set -euo pipefail

# Import the Microsoft GPG key
rpm --import https://packages.microsoft.com/keys/microsoft.asc

# Add the Visual Studio Code repository
cat > /etc/yum.repos.d/vscode.repo << 'EOF'
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

# Install Visual Studio Code
dnf install -y code