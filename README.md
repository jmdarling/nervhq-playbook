# nervhq-playbook

Local workstation setup for Fedora x86_64 and Apple Silicon macOS: desktop
applications, CLI tools, fonts, and Zsh.
Run it as the desktop user, **not root**. It installs software and changes that
user's login shell; it does not configure application accounts, sync services,
GPU drivers, gaming hardware, or dotfiles beyond the user-tool PATH block.

## Target contract and test coverage

| Target | Prerequisites | Coverage |
| --- | --- | --- |
| Fedora 44 x86_64, mutable Workstation | Python 3.14, sudo, Git; working official repositories | CI container smoke: real DNF5/bootstrap, native/COPR/vendor packages, user Flathub remote, CLI tools, verified release installers, fonts; two runs |
| Apple Silicon macOS | Python 3.14, Homebrew and Xcode Command Line Tools; OS supported by selected casks | Static validation and isolated failure tests; full Homebrew/cask/login-shell run still needs an Apple Silicon Mac |

Fedora Atomic/Silverblue/Kinoite, other distributions, Linux ARM, and Intel Macs
are outside this catalog's supported targets. The preflight rejects them before
package changes. Python **3.14** is required: Ansible core 2.21.5 fails on Python
3.15's removed `dataclasses._is_type`. Package metadata rejects incompatible
Python versions before installing tools. Do not upgrade this constraint until
Ansible supports the new controller and all checks pass.

CI does not establish that GUI apps launch or that a real login/session works.
The Fedora container smoke excludes Flatpak application installation and GUI launches.
Before using a whole catalog, run twice in a disposable desktop VM/Mac and test
application launches, log out/in, and confirm the intended login shell and PATH.

## Bootstrap

Install Python 3.14 and Git using your platform's trusted package manager. On
Fedora 44, install `python3 python3-pip git sudo`; on macOS install `python@3.14`
with Homebrew. The isolated controller does not replace the OS Python.

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

See the [software parity audit](docs/software-parity.md) for the Fedora/macOS
package matrix, version/channel differences, and confirmed choices and remaining upstream gaps.

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
# or local-macos.yml
# Repeat the same command to verify convergence.
```

Every run upgrades managed software by default. Fedora upgrades all installed
DNF packages and all installed user Flatpak apps; macOS upgrades installed Homebrew formulae
and casks. Release installers resolve the latest stable version and verify its
SHA-256. See the [exact upgrade scope and manual boundaries](docs/software-parity.md#upgrade-contract).
Use `-e workstation_upgrade_packages=false` for reviewed archive pins and package
installation without broad upgrades. No automatic reboot occurs.

Do not use `--check` as a substitute for a disposable first-run test. Interrupted
installs can be retried. Release receipts track versions and installed-file hashes,
so new versions and damaged/missing files are handled without deleting markers.

Brave Origin needs license activation on macOS. Proton Drive is intentionally
web-only on Fedora: use https://drive.proton.me in your browser. macOS retains
the desktop app. No Proton Drive CLI, browser shortcut, or PWA is installed.

ChatGPT's official Fedora preview currently requires the documented upstream
manual bootstrap; automatic installation awaits verified signing metadata.
After running on macOS, apply OS/App Store updates in System Settings/App Store.

## Package sources and user tools

- Flatpak and the Flathub remote are configured consistently in **user** scope.
  Vesktop uses its Flatpak ID on Fedora. Steam uses Flathub to avoid
  undocumented Fedora RPM Fusion prerequisites. These are
  community packages; review the [Steam Flathub page](https://flathub.org/apps/com.valvesoftware.Steam).
- Fedora uses DNF5 and installs its bindings/prerequisites. VS Code and 1Password
  use declarative vendor repositories and fingerprint-checked keys, retaining
  package signature verification. Ghostty uses the configured third-party COPR.
- macOS distinguishes Homebrew casks from formulae (Syncthing is a formula).
  Homebrew and casks may impose stricter OS requirements; inspect their current
  metadata before running. Services such as Syncthing are installed, not started.
- Volta, Fedora Starship and Nerd Fonts use verified stable release archives.
  No remote shell installer is executed. Volta goes to `~/.volta/bin` and
  Starship to `~/.local/bin`; a managed `.zshrc` block adds both to PATH.
  Starship prompt initialization is not added.
- Fedora Etcher uses its official RPM after SHA-256 verification; macOS uses its
  cask. Brave Origin uses its official signed Fedora repository and distinct cask.
- Release metadata, fallback checksums, and installed-file receipts preserve
  integrity and traceability while allowing upgrades; they do not lock all OS
  packages. See the parity audit for failure behavior and trust boundaries.

Sources: [Ansible Flatpak scope](https://docs.ansible.com/projects/ansible/latest/collections/community/general/flatpak_module.html),
[DNF5 requirements](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/dnf5_module.html),
[VS Code RPM setup](https://code.visualstudio.com/docs/setup/linux),
[1Password signing fingerprints](https://support.1password.com/install-linux/),
[Volta release](https://github.com/volta-cli/volta/releases/tag/v2.0.2),
[Starship release](https://github.com/starship/starship/releases/tag/v1.24.2),
[Nerd Fonts release/checksums](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.4.0).

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
