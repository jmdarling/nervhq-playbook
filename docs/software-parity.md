# Fedora and macOS software parity audit

Audited 2026-10-30 against the two-target repository tree in this PR. This is an
inventory of configured behavior, not a scan of Jonathan's installed machines.
No software choices were changed to force parity. Missing platform entries mean
the tasks skip that item; they do **not** prove the omission was a deliberate
product decision or that the software is unavailable on that OS.

## Decisions for Jonathan

| Priority | Decision | Evidence and recommendation |
| --- | --- | --- |
| High | Zen on Fedora versus Firefox on macOS | The `firefox` entry actually installs `app.zen_browser.zen` on Fedora. This is a different product, not just a package name. Confirm the desired browser on each OS; if the split is wanted, rename the catalog label to make it explicit. Treat the misleading label as a likely accidental documentation mismatch, not proof that Zen was accidental. |
| High | Vesktop versus Discord | The `discord` entry installs Vesktop on Fedora and the `discord` cask on macOS. Confirm whether the alternate client is wanted; if so, label/document the split explicitly. No rationale is recorded in the catalog. |
| Medium | AI tools on Fedora | `chatgpt`, `codex`, and `codex-app` exist only for macOS. Decide separately which capabilities are needed on Fedora, especially the `codex` tool versus the desktop apps. Assess available supported delivery channels only after that decision; the repository does not establish why these entries are absent. |
| Medium | Other one-platform applications | Steam is Fedora-only; balenaEtcher and Proton Drive are macOS-only. Confirm each as an OS-specific preference or record a desired alternative. Absence alone is not evidence of an upstream limitation. |
| Medium | Version parity versus native update channels | Volta is pinned to 2.0.2 on both. Fedora Starship (1.24.2) and fonts (3.4.0) are pinned, while macOS uses floating Homebrew packages. Recommend keeping native channels unless identical behavior is required, but record acceptance of version drift. |
| Medium | Scope of the upgrade switch | Fedora's switch upgrades **all DNF packages**, not just this catalog; macOS updates only selected formulae/casks. Confirm this broader Fedora maintenance policy or split system upgrades into a separately named option in a future change. |
| Medium | Empty catalogs still configure Fedora sources | Even `applications: []` leaves Flathub, vendor signing keys, and the VS Code/1Password repositories configured by bootstrap. Decide whether source setup should become conditional on selected software. No change made here. |
| Low | Git and Zsh ownership | Fedora expects Git as a bootstrap prerequisite; macOS additionally manages Git via Homebrew. Fedora installs Zsh, while macOS relies on an existing `zsh` on PATH. These mechanics are explicit, but ownership of upgrades should be confirmed; document keeping them if desired. |
| Low | Installed versus configured tools | Neither target initializes the Starship prompt, installs a Node version through Volta, starts Syncthing via explicit service tasks, or configures application accounts. Confirm these boundaries; add setup only for a requested use case. |

## Application matrix

Sources: [application catalog](../inventory/group_vars/all/applications.yml),
[Fedora dispatch](../roles/fedora/tasks/install_applications.yml), and
[macOS dispatch](../roles/macos/tasks/install_applications.yml).
`brew` in the application catalog means a **cask**, except the explicit
`brew_formula` source. All application package versions below float with their
repository/channel; `present` does not mean the two OSes get the same version.

| Catalog entry | Fedora 44 x86_64 | Apple Silicon macOS | Interpretation |
| --- | --- | --- | --- |
| `chatgpt` | Not selected | Homebrew cask `chatgpt` | One-platform selection; intent unconfirmed |
| `codex` | Not selected | Homebrew cask `codex` | One-platform selection; distinct from `codex-app`; intent unconfirmed |
| `codex-app` | Not selected | Homebrew cask `codex-app` | One-platform selection; intent unconfirmed |
| `discord` | User Flathub `dev.vencord.Vesktop` | Homebrew cask `discord` | Different clients; confirm product choice |
| `syncthing` | DNF `syncthing` | Homebrew **formula** `syncthing` | Same named software, platform packaging differs |
| `balenaetcher` | Not selected | Homebrew cask `balenaetcher` | One-platform selection; intent unconfirmed |
| `ghostty` | DNF `ghostty` from `scottames/ghostty` COPR | Homebrew cask `ghostty` | Same named software, different distributors/channels |
| `visual-studio-code` | Vendor DNF package `code` | Homebrew cask `visual-studio-code` | Package-name/source difference, not a browser-style product substitution |
| `steam` | User Flathub `com.valvesoftware.Steam` | Not selected | Fedora-only choice unconfirmed; Flathub avoids the RPM Fusion prerequisite documented in README |
| `1password` | Vendor DNF package `1password` | Homebrew cask `1password` | Same named software, platform packaging differs |
| `obsidian` | User Flathub `md.obsidian.Obsidian` | Homebrew cask `obsidian` | Same named software; install scope/channel differs |
| `proton-drive` | Not selected | Homebrew cask `proton-drive` | One-platform selection; intent unconfirmed |
| `proton-mail` | User Flathub `me.proton.Mail` | Homebrew cask `proton-mail` | Same named software; install scope/channel differs |
| `firefox` | User Flathub `app.zen_browser.zen` (Zen) | Homebrew cask `firefox` | Different products behind one misleading label |

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
| Volta | Verified Linux release archive, `~/.volta/bin` | Verified macOS release archive, `~/.volta/bin` | Both pinned 2.0.2; different platform archives/checksums; no Node/toolchain installation |
| fzf | DNF `fzf` | Homebrew formula `fzf` | Both floating; no shell integration configured |
| Stow | DNF `stow` | Homebrew formula `stow` | Both floating; no stow commands executed |
| zoxide | DNF `zoxide` | Homebrew formula `zoxide` | Both floating; no shell initialization configured |
| Starship | Verified 1.24.2 archive, `~/.local/bin/starship` | Homebrew formula `starship` | Fedora pinned, macOS floating; neither initializes the prompt |
| Zsh | DNF `zsh` | Existing executable from PATH; no catalog install | Both set the desktop user's login shell to `command -v zsh`; actual shell versions may differ |
| Fastfetch | DNF `fastfetch` | Homebrew formula `fastfetch` | Both floating; no configuration managed |
| Fira Code Nerd Font | Verified 3.4.0 archive to `~/.local/share/fonts`, then `fc-cache`; completion marker `.nervhq-firacode-3.4.0` | Homebrew cask `font-fira-code-nerd-font` | Fedora pinned/manual font-cache step; macOS floating/cask-managed |

Archive pins and checksums are in the [Fedora installers](../roles/fedora/files/)
and [macOS Volta installer](../roles/macos/files/install-volta.sh). A `creates`
marker skips an already installed script tool; changing an archive pin does not
upgrade an existing marker automatically. The package-upgrade switch does not
change that behavior. These scripts verify archive bytes, not the entire OS
package/dependency graph.

## Bootstrap, configuration, and defaults

| Area | Fedora | macOS | Evidence / meaning |
| --- | --- | --- | --- |
| Supported target | Mutable Fedora 44, x86_64; Atomic rejected | Darwin, arm64, preinstalled Homebrew; cask OS constraints still apply | [Preflight](../tasks/preflight.yml); demonstrable platform contract |
| Operator prerequisites | Python 3.14, Git, sudo and working DNF repositories | Python 3.14, Git, Homebrew and Command Line Tools per README | [Bootstrap instructions](../README.md#bootstrap); installer does not provision Python/Homebrew |
| Shared controller | Python `==3.14.*`, ansible-core 2.21.5, ansible-lint 26.10.1, community.general 13.5.0 | Same | [Project metadata](../pyproject.toml), [collection pin](../requirements.yml), [bootstrap script](../scripts/bootstrap.sh); transitive Python dependencies are not locked |
| Native prerequisites | Installs curl, tar, unzip, fontconfig, flatpak, gnupg2, python3-libdnf5, dnf5-plugins, perl-Digest-SHA | No matching bootstrap package list | [Fedora bootstrap](../roles/fedora/tasks/bootstrap.yml); platform implementation, not missing user-facing apps |
| Package sources/trust | User Flathub; fingerprint-checked Microsoft/1Password keys; vendor repositories; Ghostty COPR when selected | Existing Homebrew; formula/cask resolution delegated to Homebrew | [Vendor configuration](../roles/fedora/tasks/configure_vendor_repositories.yml); RPM package GPG checks enabled; repo metadata checks enabled for 1Password, disabled for VS Code |
| Default upgrades | DNF packages `present`; selected Flatpaks `present` | Selected formulae/casks `present`; Homebrew metadata refreshed each run | [Settings](../inventory/group_vars/all/settings.yml), [Homebrew refresh](../roles/macos/tasks/update_package_manager_cache.yml) |
| Opt-in upgrades | `workstation_upgrade_packages=true`: all DNF packages via `name: "*"`, plus selected Flatpaks to `latest` | Selected formulae/casks to `latest`; cask tasks set `greedy: true` | [Fedora upgrade task](../roles/fedora/tasks/upgrade_packages.yml); materially different update scope |
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
selects only DNF applications, leaves the full CLI/font lists in place, and
checks two runs plus installed tools/fonts and the user Flathub remote. It does
not install Flatpak applications or launch GUIs. There is no macOS runtime job.
Thus verified Fedora native installation is not evidence of functional parity
for GUI apps, sandbox permissions, macOS packages, or login sessions.

To close this audit, record Jonathan's decisions above before changing catalog
selections, and validate full desktop behavior on disposable remaining targets.
