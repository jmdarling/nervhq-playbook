# nervhq-playbook

An Ansible playbook for automated personal workstation setup on Fedora Linux and macOS.

## Overview

This playbook automates the configuration of development environments by:
- **Cross-platform support**: Automatically detects OS (Darwin/macOS vs RedHat/Fedora) and runs the appropriate role
- **Software installation**: Installs development tools, productivity apps, and entertainment software via native package managers
- **Shell configuration**: Sets Zsh as the default shell on Fedora

## Prerequisites

- **Ansible** installed on the target machine
- **Ansible Vault password** configured in `~/.ansible-vault-password`
- **Internet connection** for downloading packages
- **sudo privileges** for package installation

### Platform-specific requirements:
- **Fedora**: DNF package manager, Flatpak support
- **macOS**: Homebrew installed

## Quick Start

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd nervhq-playbook
   ```

2. Set up your vault password:
   ```bash
   echo "your_vault_password" > ~/.ansible-vault-password
   chmod 600 ~/.ansible-vault-password
   ```

3. Configure your become password in `become_password.yml`:
   ```bash
   ansible-vault edit become_password.yml
   ```

4. Run the playbook:
   ```bash
   ansible-playbook local.yml
   ```

## Software Installed

### Command Line Tools
- **fastfetch** - System information tool
- **fzf** - Fuzzy finder
- **git** - Version control
- **helix** - Text editor
- **starship** - Shell prompt
- **zsh** - Shell (set as default on Fedora)
- **zoxide** - Smart directory navigation

### Development Tools
- **Visual Studio Code** - Code editor
- **Ghostty** - Terminal emulator

### Productivity
- **Obsidian** - Note-taking application
- **1Password** - Password manager (macOS only)
- **Rectangle** - Window manager (macOS only)
- **TickTick** - Task manager (macOS only)

### Web Browsers
- **Brave Browser**
- **Firefox** (macOS only)

### Communication
- **Discord** - Chat application
- **Proton Mail** - Email client (Fedora only)

### Entertainment
- **Spotify** - Music streaming
- **VLC** - Video player
- **Steam** - Gaming platform (Fedora only)

### System Tools
- **goverlay** - Performance monitoring overlay (Fedora only)

## Repository Structure

```
nervhq-playbook/
├── ansible.cfg              # Ansible configuration
├── local.yml               # Main playbook
├── become_password.yml     # Encrypted sudo password
└── roles/
    ├── fedora/            # Fedora-specific tasks
    │   └── tasks/main.yml
    └── macos/             # macOS-specific tasks
        └── tasks/main.yml
```

## Configuration

### Vault Password
The playbook uses Ansible Vault to encrypt sensitive data. Configure your vault password in `~/.ansible-vault-password` as specified in `ansible.cfg`.

### Become Password
Your sudo password should be encrypted in `become_password.yml`:
```bash
ansible-vault edit become_password.yml
```

Add the following content:
```yaml
become_password: "your_sudo_password"
```

## Customization

### Adding Software
To add new software:
1. Edit the appropriate role file (`roles/fedora/tasks/main.yml` or `roles/macos/tasks/main.yml`)
2. Add new tasks using the appropriate package manager (DNF, Homebrew, Flatpak)

## Troubleshooting

### Common Issues
- **Permission denied**: Ensure your user has sudo privileges and the become password is correct
- **Package not found**: Some packages may not be available in all repositories; check package names and availability
- **Flatpak errors**: Ensure Flatpak is properly configured and Flathub is added as a remote

### Debugging
Run with verbose output:
```bash
ansible-playbook local.yml -vv
```

## License

This playbook is for personal use. Modify as needed for your own setup.