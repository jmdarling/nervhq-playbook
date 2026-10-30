# nervhq-playbook

An Ansible playbook for automated workstation setup.

_Note: as currently implemented, this playbook is meant to be cloned and run locally._

## What this playbook manages

This playbook:

- Installs and updates CLI tools
- Installs and updates desktop applications
- Installs fonts
- Configures the default shell (ZSH)

## Prerequisites

### Package manager

#### Arch

This playbook leverages Pacman for the majority of command line tools, Flatpak for the majority of desktop applications, and Paru to install from the AUR where the previous two do not have coverage.

##### Flatpak

Installation guide: [docs.nervhq.io](https://docs.nervhq.io/projects/homelab/NERV-HQ/Arch+workstation+setup/Steps/1.1+-+Install+Flatpak+-+Desktop+application+package+manager)

##### Paru

Installation guide: [docs.nervhq.io](<https://docs.nervhq.io/projects/homelab/NERV-HQ/Arch+workstation+setup/Steps/1.2+-+Install+Paru+-+Arch+User+Repository+(AUR)+helper>)

#### Fedora

Coming soon!

#### MacOS

This playbook leverages Homebrew for the vast majority of command line tools and desktop applications.

##### Homebrew

Installation guide: [docs.nervhq.io](https://docs.nervhq.io/projects/homelab/NERV-HQ/MacOS+workstation+setup/Steps/1.1+-+Install+Homebrew+-+Package+manager)

### Ansible

As this playbook is meant to be cloned and run locally, the full Ansible package should be installed.

#### Arch

Installation guide: [docs.nervhq.io](https://docs.nervhq.io/projects/homelab/NERV-HQ/Arch+workstation+setup/Steps/1.3+-+Install+Ansible+-+configuration+manager)

#### MacOS

Installation guide: [docs.nervhq.io](https://docs.nervhq.io/projects/homelab/NERV-HQ/MacOS+workstation+setup/Steps/1.2+-+Install+Ansible+-+Configuration+manager)

### Ansible Galaxy requirements

This playbook leverages collections and roles from [Ansible Galaxy](https://galaxy.ansible.com/ui/) that will need to be installed.

```sh
ansible-galaxy collection install -r requirements.yml
```

## Using

Each operating system has its own discrete playbook that should be run.

_Note: You will be asked to provide a "BECOME password" when executing the playbook - this is your `sudo` password._

### Arch

```sh
ansible-playbook local-arch.yml
```

### Fedora

```sh
ansible-playbook local-fedora.yml
```

### MacOS

```sh
ansible-playbook local-macos.yml
```

## Local validation

Use Python 3.14 and an isolated virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
ansible-galaxy collection install -r requirements.yml
ANSIBLE_BECOME_ASK_PASS=false ANSIBLE_ASK_PASS=false ansible-lint --offline
for script in roles/*/files/*.sh; do bash -n "$script" || exit 1; done
python -m unittest discover -s tests -v
```

These checks parse and lint the playbooks without executing workstation tasks.
CI runs these same checks with a read-only repository token.

The Arch role reserves `aur_builder` and `/etc/sudoers.d/11-install-aur_builder`
for temporary package builds. It refuses to overwrite existing resources and
removes resources it creates after normal task failures. An interrupted process,
unreachable host, or invalid task definition can still prevent cleanup; inspect
these resources manually before retrying. Do not run concurrent workstation setups.

The Volta and Starship installers and Nerd Font archive still track upstream
URLs. Downloads now fail on HTTP errors and complete before execution, but this
is not checksum verification. Review and pin upstream releases if reproducible
installer contents are required.
