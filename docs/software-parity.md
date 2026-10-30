# Fedora and macOS software parity audit

Audited 2026-10-30 against the two-target repository tree in this PR. This is an
inventory of configured behavior, not a scan of Jonathan's installed machines.
Jonathan's choices are now explicit: Brave Origin on both targets; Vesktop on
Fedora and Discord on macOS; ChatGPT as the only separately selected AI app;
Etcher, Proton Drive and Steam desired on both; upgrades enabled on every run.
The playbook does not uninstall previously selected software or change a browser
profile/default-browser setting.

## Availability and remaining decisions

- **Brave Origin:** exact product, stable `brave-origin` RPM and cask. Linux has a
  free onboarding option; macOS requires purchase/license activation by the user.
  Sources: [official Fedora instructions](https://brave.com/origin/linux/),
  [Origin licensing](https://support.brave.app/hc/en-us/articles/38561489788173-What-is-Brave-Origin),
  [Homebrew cask](https://formulae.brew.sh/cask/brave-origin).
- **ChatGPT:** macOS cask `chatgpt` selects the current official app. Separate
  Codex CLI/app entries are removed; the current ChatGPT app itself includes
  Codex capabilities, which package selection cannot remove. OpenAI now also
  supports a [Fedora 44 Linux preview](https://learn.chatgpt.com/docs/linux/linux-app).
  **Fedora automation remains blocked:** the official RPM download is known,
  but this environment could not retrieve the package/signing metadata to verify
  a safe unattended bootstrap. No guessed repository/key or unsigned fallback is
  installed. For now follow the official Fedora download/install instructions;
  its installed signed repository then participates in the all-DNF upgrade task.
  [Current macOS cask](https://formulae.brew.sh/cask/chatgpt).
- **Etcher:** an official Linux x86_64 client exists, including an RPM, so an
  alternative is unnecessary. Fedora resolves the latest stable upstream RPM
  and verifies its GitHub asset SHA-256 before installation. macOS uses the
  Apple Silicon Homebrew cask. [Upstream downloads](https://etcher-docs.balena.io/)
  and [release assets](https://github.com/balena-io/etcher/releases/latest).
- **Proton Drive:** macOS desktop app is selected. Proton lists no official Linux
  desktop sync app, but does offer an official Linux CLI. Recommended choice:
  use the web app for now; confirm whether to add the official CLI if command-line
  upload/download is useful. A CLI is not equivalent to background desktop sync.
  No unofficial wrapper is installed. [Official downloads](https://proton.me/drive/download)
  and [CLI documentation](https://proton.me/support/drive-cli).
- **Steam:** selected on both; Fedora retains its community Flathub package and
  macOS uses the [Steam cask](https://formulae.brew.sh/cask/steam). Actual game,
  controller, GPU and architecture compatibility remains outside package setup.
- **Discord:** the Vesktop/Discord split is an approved product choice, not an
  accidental omission. No account or client configuration is imposed.

## Upgrade contract

`workstation_upgrade_packages: true` is the default. Fedora refreshes and upgrades
all installed DNF packages (including the OS/kernel and configured third-party
repositories), then installs/upgrades selected native and Flatpak packages.
macOS refreshes Homebrew metadata, upgrades selected packages and all installed
Homebrew formulae/casks; greedy cask updates include self-updating applications.
Package-manager holds, disabled repositories, platform support, network failures,
and upstream publication delays still apply. Updates fail visibly rather than
silently reporting freshness. New upstream releases between runs can legitimately
produce changes; convergence means unchanged upstream releases and local inputs.

Volta on both targets, Fedora Starship and Fedora Nerd Fonts resolve the latest
stable GitHub release each run. Exact asset URLs and SHA-256 digests are checked;
older releases lacking GitHub digests have narrowly scoped reviewed fallback
checksums. Missing new-release digests fail closed. Installers keep version/digest
receipts plus installed-file hashes under `~/.local/state/nervhq`; unchanged files
skip downloads, new versions install, and missing/damaged files are repaired.
Download or verification failure does not update receipts or overwrite installed
files. These are authenticated upstream metadata checks, not independently signed
provenance. Inspect receipts to reproduce the selected version; a moving latest
channel is intentionally not a permanently locked workstation.

Etcher uses the same release/digest resolution, compares the installed RPM version,
and downloads only missing/newer versions. Its unsigned local RPM transaction
uses the verified SHA-256 instead of RPM signature checking; no global DNF setting
is changed. Temporary RPM downloads are removed even on install failure.

`-e workstation_upgrade_packages=false` disables broad package upgrades, requests
`present` from package managers, and resolves the reviewed archive pins instead
of latest releases. This is a reproducibility mode, not an absolute freeze:
missing packages still install and release scripts can converge to the reviewed pin.

**Manual boundaries:** macOS OS/App Store updates and Apple's bundled Zsh must be
applied through System Settings/App Store; Homebrew does not own them. The playbook
does not upgrade Volta-managed Node runtimes/project dependencies, application
plugins, Steam games, firmware, or software installed outside these managers.
Fedora kernel updates may require a later reboot; the playbook never reboots.
Python/Ansible controller and collection compatibility stays pinned to Python
3.14 and the reviewed tooling versions; ordinary app updates do not change it.
This scope must not be described as a guarantee that every byte on a machine is
updated. macOS system updates may require interactive owner authentication and
remain an explicit post-run step.

## Application matrix

Sources: [application catalog](../inventory/group_vars/all/applications.yml),
[Fedora dispatch](../roles/fedora/tasks/install_applications.yml), and
[macOS dispatch](../roles/macos/tasks/install_applications.yml).
`brew` in the application catalog means a **cask**, except the explicit
`brew_formula` source. All application package versions below float with their
repository/channel; `present` does not mean the two OSes get the same version.

| Catalog entry | Fedora 44 x86_64 | Apple Silicon macOS | Interpretation |
| --- | --- | --- | --- |
| `chatgpt` | Official preview; manual bootstrap pending verification above | Homebrew cask `chatgpt` | Only selected AI app; includes upstream Codex features |
| `discord` | User Flathub `dev.vencord.Vesktop` | Homebrew cask `discord` | Different clients; intentionally approved |
| `syncthing` | DNF `syncthing` | Homebrew **formula** `syncthing` | Same named software, platform packaging differs |
| `balenaetcher` | Official release RPM, verified SHA-256 | Homebrew cask `balenaetcher` | Both selected, platform-native distributions |
| `ghostty` | DNF `ghostty` from `scottames/ghostty` COPR | Homebrew cask `ghostty` | Same named software, different distributors/channels |
| `visual-studio-code` | Vendor DNF package `code` | Homebrew cask `visual-studio-code` | Package-name/source difference, not a browser-style product substitution |
| `steam` | User Flathub `com.valvesoftware.Steam` | Homebrew cask `steam` | Both selected; different packaging channels |
| `1password` | Vendor DNF package `1password` | Homebrew cask `1password` | Same named software, platform packaging differs |
| `obsidian` | User Flathub `md.obsidian.Obsidian` | Homebrew cask `obsidian` | Same named software; install scope/channel differs |
| `proton-drive` | Desktop app unavailable; web/official CLI options above | Homebrew cask `proton-drive` | Desired parity blocked by desktop availability |
| `proton-mail` | User Flathub `me.proton.Mail` | Homebrew cask `proton-mail` | Same named software; install scope/channel differs |
| `brave-origin` | Official stable DNF `brave-origin` | Homebrew cask `brave-origin` | Exact same product; macOS license activation required |

## CLI tools and fonts

Sources: [CLI catalog](../inventory/group_vars/all/cli_tools.yml),
[font catalog](../inventory/group_vars/all/fonts.yml),
[Fedora CLI tasks](../roles/fedora/tasks/install_cli_tools.yml),
[macOS CLI tasks](../roles/macos/tasks/install_cli_tools.yml), and font tasks for
[Fedora](../roles/fedora/tasks/install_fonts.yml) / [macOS](../roles/macos/tasks/install_fonts.yml).

| Entry | Fedora | macOS | Version/configuration difference |
| --- | --- | --- | --- |
| Git | Required before bootstrap; no Fedora catalog entry | Homebrew formula `git` | Explicit prerequisite versus managed package |
| Neovim | DNF `neovim` | Homebrew formula `neovim` | Both floating; no editor configuration managed |
| Volta | Verified Linux release archive, `~/.volta/bin` | Verified macOS release archive, `~/.volta/bin` | Both latest stable; different platform archives/checksums; no Node/toolchain installation |
| fzf | DNF `fzf` | Homebrew formula `fzf` | Both floating; no shell integration configured |
| Stow | DNF `stow` | Homebrew formula `stow` | Both floating; no stow commands executed |
| zoxide | DNF `zoxide` | Homebrew formula `zoxide` | Both floating; no shell initialization configured |
| Starship | Verified latest stable archive, `~/.local/bin/starship` | Homebrew formula `starship` | Both floating through different channels; neither initializes the prompt |
| Zsh | DNF `zsh` | Existing executable from PATH; no catalog install | Both set the desktop user's login shell to `command -v zsh`; actual shell versions may differ |
| Fastfetch | DNF `fastfetch` | Homebrew formula `fastfetch` | Both floating; no configuration managed |
| Fira Code Nerd Font | Verified latest stable archive to `~/.local/share/fonts`, then `fc-cache` | Homebrew cask `font-fira-code-nerd-font` | Fedora release receipt/manual font-cache step; macOS floating/cask-managed |

Release metadata and reviewed fallback checksums live in the
[release catalog](../inventory/group_vars/all/releases.yml); shared resolution is
in [release tasks](../roles/common/tasks/resolve_release.yml). Install scripts
verify bytes and installed-file manifests. This does not lock OS dependencies.

## Bootstrap, configuration, and defaults

| Area | Fedora | macOS | Evidence / meaning |
| --- | --- | --- | --- |
| Supported target | Mutable Fedora 44, x86_64; Atomic rejected | Darwin, arm64, preinstalled Homebrew; cask OS constraints still apply | [Preflight](../tasks/preflight.yml); demonstrable platform contract |
| Operator prerequisites | Python 3.14, Git, sudo and working DNF repositories | Python 3.14, Git, Homebrew and Command Line Tools per README | [Bootstrap instructions](../README.md#bootstrap); installer does not provision Python/Homebrew |
| Shared controller | Python `==3.14.*`, ansible-core 2.21.5, ansible-lint 26.10.1, community.general 13.5.0 | Same | [Project metadata](../pyproject.toml), [collection pin](../requirements.yml), [bootstrap script](../scripts/bootstrap.sh); transitive Python dependencies are not locked |
| Native prerequisites | Installs curl, tar, unzip, fontconfig, flatpak, gnupg2, python3-libdnf5, dnf5-plugins, perl-Digest-SHA | No matching bootstrap package list | [Fedora bootstrap](../roles/fedora/tasks/bootstrap.yml); platform implementation, not missing user-facing apps |
| Package sources/trust | User Flathub; fingerprint-checked Microsoft/1Password/Brave keys; vendor repositories; Ghostty COPR when selected | Existing Homebrew; formula/cask resolution delegated to Homebrew | [Vendor configuration](../roles/fedora/tasks/configure_vendor_repositories.yml); RPM package GPG checks enabled; repo metadata checks enabled for 1Password, disabled for VS Code |
| Default upgrades | All DNF packages; selected Flatpaks and release installers | All installed Homebrew formulae/casks; Volta latest stable | [Settings](../inventory/group_vars/all/settings.yml), [Homebrew refresh](../roles/macos/tasks/update_package_manager_cache.yml) |
| Privilege/scope | DNF/repository/shell changes use sudo; Flatpak, user tools, fonts and PATH run as desktop user | Homebrew tasks run as desktop user; login-shell change uses sudo | Platform role tasks; no global become on either entrypoint |
| Shell/PATH | Zsh selected from PATH; managed `.zshrc` exports `VOLTA_HOME` and prepends Volta plus `~/.local/bin` | Same | [Shared configuration](../tasks/user_environment.yml); no Starship/zoxide/fzf initialization or Homebrew `shellenv` setup |
| Services/accounts | No explicit service enable/start or application-login tasks | Same | Role task lists; package-manager postinstall side effects are outside this guarantee |

The [localhost inventory](../inventory/hosts.yml) selects local execution using
the controller interpreter on both platforms. DNF5 can respawn using system
bindings. The entrypoints run preflight, then the platform role, then the shared
user-environment task. Fedora configures vendor repositories before installation
and reconciles them afterward because RPM postinstall scripts can rewrite them.

## Optional selections and validation limits

There are no per-application enable flags. Missing OS mappings are skipped.
`-e @my-workstation.yml` replaces whole `applications`, `cli_tools`, or `fonts`
lists; it does not merge them. The defaults include every mapped item. Removing
an entry does not uninstall software already present. The generic application
script handlers can use sudo, but neither default application catalog selects
that source; CLI/font scripts currently run without sudo.

Bootstrap source setup is unconditional on Fedora: empty application lists do
not suppress Flatpak prerequisites, the user Flathub remote, or vendor sources.
On macOS, Homebrew metadata refresh and login-shell configuration still run with
empty package lists. Both always run the shared PATH task. A custom Fedora CLI
list must keep Zsh or ensure it already exists for the shell step.

[CI](../.github/workflows/validate.yml) lints both target trees and runs the
remaining regression tests. The [Fedora smoke test](../tests/fedora-smoke.sh)
selects DNF and verified release-RPM applications, leaves the full CLI/font lists in place, and
checks two runs plus installed tools/fonts and the user Flathub remote. It does
not install Flatpak applications or launch GUIs. There is no macOS runtime job.
Thus verified Fedora native installation is not evidence of functional parity
for GUI apps, sandbox permissions, macOS packages, or login sessions.

Remaining review: Proton Drive CLI versus web-only Fedora use, verified ChatGPT
Fedora bootstrap, and full desktop validation on disposable Fedora/macOS targets.
