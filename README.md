# nervhq-playbook

Local workstation setup for desktop applications, CLI tools, fonts, and Zsh.
Run it as the desktop user, **not root**. It installs software and changes that
user's login shell; it does not configure application accounts, sync services,
GPU drivers, gaming hardware, or dotfiles beyond the user-tool PATH block.

## Target contract and test coverage

| Target | Prerequisites | Coverage |
| --- | --- | --- |
| Fedora 44 x86_64, mutable Workstation | Python 3.14, sudo, Git; working official repositories | CI container smoke: real DNF5/bootstrap, signed vendor repositories, user Flathub remote, Zsh, fzf, Volta, Starship, fonts; two runs |
| Arch Linux x86_64 | Python 3.14 controller, sudo, working Pacman mirrors, preinstalled Paru | Static validation and isolated failure tests; full AUR/desktop run still needs a disposable Arch VM |
| Apple Silicon macOS | Python 3.14, Homebrew and Xcode Command Line Tools; OS supported by selected casks | Static validation and isolated failure tests; full Homebrew/cask/login-shell run still needs an Apple Silicon Mac |

Fedora Atomic/Silverblue/Kinoite, other distributions, Linux ARM, and Intel Macs
are outside this catalog's supported targets. The preflight rejects them before
package changes. Python **3.14** is required: Ansible core 2.21.5 fails on Python
3.15's removed `dataclasses._is_type`. Package metadata rejects incompatible
Python versions before installing tools. Do not upgrade this constraint until
Ansible supports the new controller and all checks pass.

CI does not establish that GUI apps launch or that a real login/session works.
The Fedora container smoke deliberately excludes GUI applications and COPR.
Before using a whole catalog, run twice in a disposable desktop VM/Mac and test
application launches, log out/in, and confirm the intended login shell and PATH.

## Bootstrap

Install Python 3.14 and Git using your platform's trusted package manager. On
Fedora 44, install `python3 python3-pip git sudo`; on macOS install `python@3.14`
with Homebrew. On rolling Arch, use an already trusted Python 3.14 installation
if the system Python has moved on. The isolated controller does not replace the
OS Python. Install/review Paru before starting Arch (this playbook does not
blindly build an AUR helper). See [Paru's instructions](https://github.com/Morganamilo/paru#installation).

Clone this repository, then from its root:

```sh
bash scripts/bootstrap.sh
# If Python 3.14 has another executable name/path:
# PYTHON=/path/to/python3.14 bash scripts/bootstrap.sh
. .venv/bin/activate
ansible-inventory --host localhost
```

The bootstrap checks Python first, creates `.venv`, installs pinned Ansible
core/lint, and installs the exact collections in `requirements.yml`. It does not
execute workstation tasks. All commands below run from the repository root.
`inventory/hosts.yml` explicitly selects localhost and uses the controller's
interpreter. Local module execution therefore uses Python 3.14; DNF5 may respawn
with the OS interpreter to access `python3-libdnf5`.

## Review, customize, run

Review `inventory/group_vars/all/{applications,cli_tools,fonts}.yml` before use.
Each entry declares its source per OS; an absent OS entry is intentionally
skipped. You can supply replacement lists via `-e @my-workstation.yml`. Lists
replace the defaults rather than merging with them. For example:

```yaml
applications: []
fonts: []
cli_tools:
  - name: zsh
    fedora:
      source: dnf
```

Run the matching playbook as your desktop user. `--ask-become-pass` requests your
sudo password; omit it only when your existing sudo policy needs no password.

```sh
ansible-playbook local-fedora.yml --ask-become-pass
# or local-arch.yml / local-macos.yml
# Repeat the same command to verify convergence.
```

Ordinary runs install missing packages (`state: present`). For deliberate package
updates use `-e workstation_upgrade_packages=true`. **Arch is an exception:** its
bootstrap always refreshes repositories and performs a full Pacman upgrade,
because partial upgrades are unsupported. AUR upgrades remain opt-in. Homebrew
metadata is refreshed on each run; it is not a promise of a zero-change recap.

Do not use `--check` as a substitute for a disposable first-run test: prerequisites,
new repositories, temporary users, and installer scripts can make a first dry run
incomplete. Interrupted installs can be retried. If a marker binary/font already
exists, scripts are skipped; remove the relevant marker deliberately to reinstall
or apply a future archive pin change. The playbook does not downgrade existing
tools or overwrite their state simply because a pin changed.

## Package sources and user tools

- Flatpak and the Flathub remote are configured consistently in **user** scope.
  Vesktop uses its Flatpak ID on both Linux targets. Steam uses Flathub to avoid
  undocumented Arch multilib and Fedora RPM Fusion prerequisites. These are
  community packages; review the [Steam Flathub page](https://flathub.org/apps/com.valvesoftware.Steam).
- Fedora uses DNF5 and installs its bindings/prerequisites. VS Code and 1Password
  use declarative vendor repositories and fingerprint-checked keys, retaining
  package signature verification. Ghostty uses the configured third-party COPR.
- macOS distinguishes Homebrew casks from formulae (Syncthing is a formula).
  Homebrew and casks may impose stricter OS requirements; inspect their current
  metadata before running. Services such as Syncthing are installed, not started.
- Volta **2.0.2**, Fedora Starship **1.24.2**, and Fira Code Nerd Font **3.4.0**
  download fixed release archives and verify embedded SHA-256 digests before
  extraction. No remote shell installer is executed. Volta goes to `~/.volta/bin`
  and Starship to `~/.local/bin`, without sudo. A managed `.zshrc` block adds both
  directories to PATH. Starship prompt initialization is optional and not added.
- Binary/Font pins are reproducible downloads, not a lock of the whole workstation:
  DNF, Pacman, AUR, Flatpak, Homebrew and COPR remain moving repositories.
  Before updating a pin, inspect the upstream release and independently verify
  the archive digest, then run the archive and container tests.

Sources: [Ansible Flatpak scope](https://docs.ansible.com/projects/ansible/latest/collections/community/general/flatpak_module.html),
[DNF5 requirements](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/dnf5_module.html),
[VS Code RPM setup](https://code.visualstudio.com/docs/setup/linux),
[1Password signing fingerprints](https://support.1password.com/install-linux/),
[Volta release](https://github.com/volta-cli/volta/releases/tag/v2.0.2),
[Starship release](https://github.com/starship/starship/releases/tag/v1.24.2),
[Nerd Fonts release/checksums](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.4.0).

## Arch temporary builder

The Arch role reserves `aur_builder` and `/etc/sudoers.d/11-install-aur_builder`.
It refuses existing resources, creates a temporary account with Pacman-only sudo,
imports the fingerprint-verified 1Password AUR key, and removes its account,
home/keyring and sudoers access after normal task failures. Account creation and
cleanup are real changes and are reported honestly on every Arch run. AUR build
recipes execute as that temporary account and must be trusted/reviewed by the
operator; no AUR recipes are built in CI.

Do not run concurrent setups. Interruption, an unreachable host, or an invalid
task definition can still prevent cleanup. Inspect those reserved resources
before retrying; do not delete a pre-existing account blindly.

## Validation

```sh
. .venv/bin/activate
ansible-lint --offline
for script in roles/*/files/*.sh scripts/*.sh tests/*.sh; do bash -n "$script" || exit 1; done
python -m unittest discover -s tests -v
```

Tests use temporary homes, fake failed/corrupt downloads, inventory loading,
preflight refusal, and actual Ansible repeat runs on isolated user configuration.
They do not run the workstation roles against your machine. CI additionally runs
`tests/fedora-smoke.sh` **inside a disposable Fedora container**; never invoke
that script on a host. It installs tools/packages and creates a test user only
inside that container. Workflows have read-only repository permissions and no
deployment steps or live host access.
