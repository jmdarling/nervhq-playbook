# nervhq-playbook

Local workstation setup for Fedora x86_64 and Apple Silicon macOS: desktop
applications, CLI tools, fonts, and Zsh.
Run it as the desktop user, **not root**. It installs software and changes that
user's login shell; it does not configure application accounts, sync services,
GPU drivers, gaming hardware, or dotfiles beyond the user-tool PATH and mise blocks.

## Target contract and test coverage

| Target | Prerequisites | Coverage |
| --- | --- | --- |
| Fedora x86_64, mutable Workstation | Fedora's `ansible` package and normal desktop-user sudo access; working official repositories | Fedora 44/45 CI matrix exercises system Ansible, real DNF/bootstrap, native/COPR/vendor packages, user Flathub remote, CLI tools, verified release installers and fonts; two runs |
| Apple Silicon macOS | Working Ansible, Homebrew and Xcode Command Line Tools; OS supported by selected casks | Static validation and isolated failure tests; full Homebrew/cask/login-shell run still needs an Apple Silicon Mac |

Fedora Atomic/Silverblue/Kinoite, Arch Linux, other distributions, Linux ARM, and Intel Macs
are outside this catalog's supported targets. The preflight rejects them before
package changes. Use the Python supported by your installed Ansible, including
Fedora 45's system Python. The playbook does not require a separate Python
installation, pip, a virtualenv, or lint tooling. The playbook checks the actual
platform and package-manager capabilities, not OS, Python or Ansible version numbers.
Newer or older releases are not rejected merely because they are outside the CI
matrix. Availability of vendor packages and compatibility with the installed
Ansible remain upstream constraints.

The tools in [project metadata](pyproject.toml) are optional **development
validation** dependencies, not workstation runtime prerequisites. Their Python
minimum follows the pinned Ansible toolchain; CI tests Python 3.13, 3.14 and 3.15
separately from the system-Ansible smoke tests.

CI does not establish that GUI apps launch or that a real login/session works.
The Fedora container smoke excludes Flatpak application installation and GUI launches.
Before using a whole catalog, run twice in a disposable desktop VM/Mac and test
application launches, log out/in, and confirm the intended login shell and PATH.

## Run on a fresh Fedora installation

As your normal desktop user, install Ansible with Fedora's package manager:

```sh
sudo dnf install ansible
```

Download and extract this repository (or clone it if Git is already installed),
then run from its root:

```sh
ansible-playbook local-fedora.yml --ask-become-pass
```

That is the workstation entry point. No bootstrap script, virtualenv activation,
`pip` or manual `ansible-galaxy` command is required. The playbook installs Git
and its other native prerequisites itself. Normal Fedora Workstation already
provides sudo; the desktop user must be allowed to use it.

The full Ansible package supplies `community.general`, which is still needed
for Flatpak and Homebrew. A core-only installation receives an early diagnostic
to install full Ansible, before package changes. No collection is installed or
upgraded during a workstation run. `inventory/hosts.yml` selects localhost and
the running Ansible interpreter; DNF can respawn under the OS interpreter to
use its Python bindings.

## Optional development bootstrap

For contributors who want the pinned lint/test tools, use Python 3.13+ and
run the following from the repository root. This is not needed to provision Fedora.
On macOS, it is also one way to install Ansible after setting up Homebrew and
Xcode Command Line Tools.

```sh
bash scripts/bootstrap.sh
# If your preferred Python has another executable name/path:
# PYTHON=/path/to/python3 bash scripts/bootstrap.sh
. .venv/bin/activate
```

The development bootstrap creates `.venv`, installs pinned Ansible core/lint, and
installs the exact collections in `requirements.yml`. It does not execute workstation tasks.

## Review, customize, run

See the [software parity audit](docs/software-parity.md) for the Fedora/macOS
package matrix, version/channel differences, confirmed choices, and validation limits.

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
# On macOS instead:
# ansible-playbook local-macos.yml --ask-become-pass
# Repeat the same command to verify convergence.
```

Every run upgrades managed software by default. Fedora upgrades all installed
DNF packages and all installed user Flatpak apps; macOS upgrades installed Homebrew formulae
and casks. Release installers resolve the latest stable version and verify its
SHA-256. See the [exact upgrade scope and manual boundaries](docs/software-parity.md#upgrade-contract).
Use `-e '{"workstation_upgrade_packages": false}'` for reviewed archive pins and package
installation without broad upgrades. No automatic reboot occurs.

Do not use `--check` as a substitute for a disposable first-run test. Interrupted
installs can be retried. Release receipts track versions and installed-file hashes,
so new versions and damaged/missing files are handled without deleting markers.

Brave Origin needs license activation on macOS. Proton Drive is intentionally
web-only on Fedora: use https://drive.proton.me in your browser. macOS retains
the desktop app. No Proton Drive CLI, browser shortcut, or PWA is installed.

ChatGPT is the only separately selected AI app; separate Codex CLI/app packages
are not selected. ChatGPT itself includes upstream Codex capabilities.
ChatGPT's official Fedora preview bootstraps from a pinned, hash- and signature-verified
RPM, then receives updates from OpenAI's signed DNF repository. See the
[verification contract](docs/software-parity.md#chatgpt-fedora-bootstrap).
After running on macOS, apply OS/App Store updates in System Settings/App Store.

## Package sources and user tools

- Flatpak and the Flathub remote are configured consistently in **user** scope.
  Vesktop on Fedora and Discord on macOS are an intentional client split.
  Steam uses Flathub on Fedora to avoid
  undocumented Fedora RPM Fusion prerequisites. These are
  community packages; review the [Steam Flathub page](https://flathub.org/apps/com.valvesoftware.Steam).
- Fedora uses the detected DNF backend and installs its bindings/prerequisites. VS Code and 1Password
  use declarative vendor repositories and fingerprint-checked keys, retaining
  package signature verification. Ghostty uses the configured third-party COPR.
- macOS distinguishes Homebrew casks from formulae (Syncthing is a formula).
  Homebrew and casks may impose stricter OS requirements; inspect their current
  metadata before running. Services such as Syncthing are installed, not started.
- Fedora mise, Starship and Nerd Fonts use verified stable release archives.
  No remote shell installer is executed. mise and Starship go to `~/.local/bin`;
  macOS installs mise through Homebrew. Managed Zsh blocks add user tools to
  PATH, activate mise in `.zshrc`, and expose shims in `.zprofile` for login shells.
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
[mise release](https://github.com/jdx/mise/releases/tag/v2026.10.25),
[Starship release](https://github.com/starship/starship/releases/tag/v1.24.2),
[Nerd Fonts release/checksums](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.4.0).

## Node environment

Selecting mise in the CLI catalog also configures the desktop user's global
`node = "lts"` request, installs Node and its bundled npm, and rebuilds command
shims. The alias stays floating; normal runs install the newest available LTS,
including a new LTS major when upstream promotes it. With
`workstation_upgrade_packages: false`, an installed matching LTS version is reused;
missing Node installations are still provisioned. Other global mise tools and
settings are preserved. No separate npm, pnpm or Yarn version is selected.

Interactive Zsh uses `mise activate zsh`; login shells use
`mise activate zsh --shims`. The macOS blocks also expose Homebrew's binary
directory so `mise` itself is available. Start a new shell after provisioning and restart
editors that inherited the old PATH. Jobs that do not inherit a login environment
can use `mise exec -- node ...`. See the upstream [shell setup](https://mise.jdx.dev/shell-setup.html)
and [Node documentation](https://mise.jdx.dev/lang/node.html).

Project-specific mise configurations can override the global default. The
playbook does not rewrite project version files, migrate global Volta packages,
or delete existing Volta installations. It replaces its own managed Volta PATH
block; remove any separately configured Volta activation when migrating an older
workstation. Removing mise from the CLI catalog skips its runtime configuration
and shell activation.

## Podman development tool

The CLI catalog installs Fedora's native `podman` package and the Apple Silicon
Homebrew **formula** `podman`, using the existing package upgrade policy.
[Fedora/upstream installation instructions](https://podman.io/docs/installation)
and the [Homebrew formula](https://formulae.brew.sh/formula/podman) describe these
sources. Upstream recommends its macOS installer over community-maintained
Homebrew; this repository uses Homebrew consistently with its other CLI tools.

After installation, `podman --version` and `podman --help` check the CLI without
starting a workload. The playbook does not create/start machines or containers,
enable services/sockets, install Podman Desktop or Docker compatibility, or
modify user groups, subordinate ID ranges, networking or security settings.

On Fedora, use Podman as your desktop user. Before first use, confirm that
`/etc/subuid` and `/etc/subgid` contain valid, non-overlapping ranges for that user,
that `newuidmap`/`newgidmap` are available, and that user namespaces are permitted.
Rootless networking needs `pasta` (Fedora's `passt` package); keep normal DNF
runtime dependencies enabled. Local container storage is needed: NFS-backed
storage is unsupported. Resolve missing prerequisites with the administrator
rather than changing security policy or inventing UID ranges in this playbook.
See [upstream rootless requirements](https://docs.podman.io/en/latest/markdown/podman.1.html#rootless-mode).
After that review, run `podman info` manually to validate the host environment.

On macOS, container execution requires a Linux VM. When ready to allocate VM
resources and download its image, run these commands yourself as your normal user:

```sh
podman machine init
podman machine start
podman info
# Stop it when finished:
podman machine stop
```

Homebrew upgrades the host CLI, not an existing VM's guest OS or container images.
Review the [machine update instructions](https://docs.podman.io/en/latest/markdown/podman-machine-init.1.html)
after host upgrades: mismatched host/guest Podman versions are unsupported.
VM updates, image refreshes, registry login, Compose providers and development
workloads remain manual. No VM is needed for native Fedora container execution.

The Fedora smoke script includes CLI version/help checks and two package runs;
these checks validate installation and convergence, not rootless workload
execution. No container workload or macOS VM test is claimed.

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

The [previous implementation CI run](https://github.com/jmdarling/nervhq-playbook/actions/runs/41152587189)
installed ChatGPT `26.1027.30824-1.x86_64` in a disposable Fedora container,
verified its installed files with `rpm -V`, and completed a second full run with
`changed=0, failed=0`. It also passed lint, shell checks and all nine tests.
That run predates the mise migration. The updated smoke test additionally checks
Node/npm in fresh login and interactive Zsh sessions and the global LTS request;
it still needs a new CI run. No desktop launch or real login-session test is claimed.
