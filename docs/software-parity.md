# Fedora and macOS software parity audit

Audited 2026-10-31 against the two-target repository tree in this PR. This is an
inventory of configured behavior, not a scan of Jonathan's installed machines.
Jonathan's choices are now explicit: Brave Origin on both targets; Vesktop on
Fedora and Discord on macOS; ChatGPT as the only separately selected AI app;
Etcher and Steam on both; Proton Drive web-only on Fedora and the desktop app
on macOS; upgrades enabled on every run.
The playbook does not uninstall previously selected software or change a browser
profile/default-browser setting.

## Confirmed selections and availability

- **Brave Origin:** exact product, stable `brave-origin` RPM and cask. Linux has a
  free onboarding option; macOS requires purchase/license activation by the user.
  Sources: [official Fedora instructions](https://brave.com/origin/linux/),
  [Origin licensing](https://support.brave.app/hc/en-us/articles/38561489788173-What-is-Brave-Origin),
  [Homebrew cask](https://formulae.brew.sh/cask/brave-origin).
- **ChatGPT:** macOS cask `chatgpt` selects the current official app. Separate
  Codex CLI/app entries are removed; the current ChatGPT app itself includes
  Codex capabilities, which package selection cannot remove. OpenAI now also
  supports a [Fedora 44 Linux preview](https://learn.chatgpt.com/docs/linux/linux-app).
  Fedora now bootstraps a verified official RPM before routine DNF upgrades.
  The installed signed OpenAI repository supplies subsequent versions; the
  bootstrap pin does not cap routine upgrades. No application is launched or
  account configured by the playbook. See the verification contract below.
  [Current macOS cask](https://formulae.brew.sh/cask/chatgpt).
- **Etcher:** an official Linux x86_64 client exists, including an RPM, so an
  alternative is unnecessary. Fedora resolves the latest stable upstream RPM
  and verifies its GitHub asset SHA-256 before installation. macOS uses the
  Apple Silicon Homebrew cask. [Upstream downloads](https://etcher-docs.balena.io/)
  and [release assets](https://github.com/balena-io/etcher/releases/latest).
- **Proton Drive:** Jonathan explicitly chose web-only access on Fedora after
  reviewing the CLI's purpose. Use [the web app](https://drive.proton.me) in the
  existing browser. macOS retains the official desktop app. This is an intentional
  platform difference; no CLI, unofficial wrapper, browser shortcut, PWA, or
  background synchronization service is installed on Fedora. Proton documents
  the CLI for explicit transfers and scripted workflows; it is not selected here.
  [Official downloads](https://proton.me/drive/download) and
  [CLI documentation](https://proton.me/support/drive-cli).
- **Steam:** selected on both; Fedora retains its community Flathub package and
  macOS uses the [Steam cask](https://formulae.brew.sh/cask/steam). Actual game,
  controller, GPU and architecture compatibility remains outside package setup.
- **Discord:** the Vesktop/Discord split is an approved product choice, not an
  accidental omission. No account or client configuration is imposed.

## Upgrade contract

`workstation_upgrade_packages: true` is the default. Fedora refreshes and upgrades
all installed DNF packages (including the OS/kernel and configured third-party
repositories), then installs/upgrades selected native packages and all installed user Flatpak apps.
macOS refreshes Homebrew metadata, upgrades selected packages and all installed
Homebrew formulae/casks; greedy cask updates include self-updating applications.
Podman host packages follow these upgrades; container images, workloads and any
macOS Podman machine guest OS are outside this policy. A host upgrade can require
a manual guest update before use; see [Podman first use](../README.md#podman-development-tool).
Package-manager holds, disabled repositories, platform support, network failures,
and upstream publication delays still apply. Updates fail visibly rather than
silently reporting freshness. New upstream releases between runs can legitimately
produce changes; convergence means unchanged upstream releases and local inputs.

Fedora mise, Starship and Nerd Fonts resolve the latest
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

`-e '{"workstation_upgrade_packages": false}'` disables broad package upgrades, requests
`present` from package managers, and resolves the reviewed archive pins instead
of latest releases. This is a reproducibility mode, not an absolute freeze:
missing packages still install and release scripts can converge to the reviewed pin.
The global mise Node request remains `lts`: ordinary runs refresh to the newest
LTS, while upgrade-disabled runs reuse an installed matching version or install
it if missing. Node includes npm; other global tools/settings are preserved.

**Manual boundaries:** macOS OS/App Store updates and Apple's bundled Zsh must be
applied through System Settings/App Store; Homebrew does not own them. The playbook
does not upgrade project dependencies or project-pinned Node runtimes, application
plugins, Steam games, firmware, or software installed outside these managers.
Fedora kernel updates may require a later reboot; the playbook never reboots.
The playbook uses the installed Ansible and its supported Python, with no runtime
version-number gates. The full Ansible package provides `community.general`;
core-only installs receive an early diagnostic instead of failing later during
role parsing. The optional development environment uses the reviewed tooling
versions in `pyproject.toml`; its Python minimum follows
those tools, not an arbitrary minor-version allowlist. CI exercises Python
3.13, 3.14 and 3.15.
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

| Catalog entry | Fedora 44/45 x86_64 | Apple Silicon macOS | Interpretation |
| --- | --- | --- | --- |
| `chatgpt` | Verified official RPM bootstrap, then signed OpenAI DNF repository | Homebrew cask `chatgpt` | Only selected AI app; includes upstream Codex features |
| `discord` | User Flathub `dev.vencord.Vesktop` | Homebrew cask `discord` | Different clients; intentionally approved |
| `syncthing` | DNF `syncthing` | Homebrew **formula** `syncthing` | Same named software, platform packaging differs |
| `balenaetcher` | Official release RPM, verified SHA-256 | Homebrew cask `balenaetcher` | Both selected, platform-native distributions |
| `ghostty` | DNF `ghostty` from `scottames/ghostty` COPR | Homebrew cask `ghostty` | Same named software, different distributors/channels |
| `visual-studio-code` | Vendor DNF package `code` | Homebrew cask `visual-studio-code` | Package-name/source difference, not a browser-style product substitution |
| `steam` | User Flathub `com.valvesoftware.Steam` | Homebrew cask `steam` | Both selected; different packaging channels |
| `1password` | Vendor DNF package `1password` | Homebrew cask `1password` | Same named software, platform packaging differs |
| `obsidian` | User Flathub `md.obsidian.Obsidian` | Homebrew cask `obsidian` | Same named software; install scope/channel differs |
| `proton-drive` | Web-only at `drive.proton.me`; no installed package | Homebrew cask `proton-drive` | Intentional web/desktop split approved by Jonathan |
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
| Podman | Official Fedora DNF `podman` | Homebrew formula `podman` | Floating package versions; native Linux versus manually initialized Linux VM; see [first use](../README.md#podman-development-tool) |
| Neovim | DNF `neovim` | Homebrew formula `neovim` | Both floating; no editor configuration managed |
| mise / Node | Verified Linux mise archive, `~/.local/bin/mise` | Homebrew formula `mise` | Global `node = "lts"`, Node plus bundled npm; default runs refresh LTS; mise versions may differ by source |
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
| Supported target | Mutable Fedora, x86_64; Atomic rejected | Darwin, arm64, preinstalled Homebrew; cask OS constraints still apply | [Preflight](../tasks/preflight.yml); demonstrable platform contract |
| Operator prerequisites | System Ansible, normal desktop sudo access and working DNF repositories | Ansible, Homebrew and Command Line Tools per README | [First-run instructions](../README.md#run-on-a-fresh-fedora-installation); Fedora installs Git and native prerequisites itself |
| Development controller | Python `>=3.13`, full Ansible 15.0.0b1 with bundled collections, ansible-core 2.22.0 and ansible-lint 26.11.0; optional for workstation runs | Same | [Project metadata](../pyproject.toml), [bootstrap script](../scripts/bootstrap.sh); transitive Python dependencies are not locked |
| Native prerequisites | Installs a curl provider, tar, gzip, unzip, fontconfig, flatpak, gnupg2 and the detected DNF backend's Python binding | No matching bootstrap package list | [Fedora bootstrap](../roles/fedora/tasks/bootstrap.yml); platform implementation, not missing user-facing apps |
| Package sources/trust | User Flathub; fingerprint-checked Microsoft/1Password/Brave keys; verified OpenAI bootstrap when selected; vendor repositories; Ghostty COPR when selected | Existing Homebrew; formula/cask resolution delegated to Homebrew | [Vendor configuration](../roles/fedora/tasks/configure_vendor_repositories.yml); RPM package GPG checks enabled except checksum-verified Etcher; repo metadata checks enabled for 1Password/OpenAI, disabled for VS Code/Brave |
| Default upgrades | All DNF packages; all installed user Flatpak apps and release installers; global Node LTS | All installed Homebrew formulae/casks; global Node LTS | [Settings](../inventory/group_vars/all/settings.yml), [Homebrew refresh](../roles/macos/tasks/update_package_manager_cache.yml) |
| Privilege/scope | DNF/repository/shell changes use sudo; Flatpak, user tools, fonts and PATH run as desktop user | Homebrew tasks run as desktop user; login-shell change uses sudo | Platform role tasks; no global become on either entrypoint |
| Shell/PATH | Zsh selected from PATH; `.zshrc` adds user tools and activates mise; `.zprofile` exposes user tools and mise shims | Same; activation uses the Apple Silicon Homebrew mise path | [Shared configuration](../tasks/user_environment.yml); no Starship/zoxide/fzf initialization or Homebrew `shellenv` setup |
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

Fedora baseline source setup is unconditional: empty application lists do not
suppress Flatpak prerequisites, the user Flathub remote, or VS Code/1Password/Brave
sources. ChatGPT bootstrap is conditional on selecting its Fedora DNF entry;
Ghostty COPR is configured only when selected.
On macOS, Homebrew metadata refresh and login-shell configuration still run with
empty package lists. Both always run the shared PATH task. Global Node installation
and mise activation run only when mise is selected for the target. Existing
Volta binaries/packages and independently configured shell blocks are not removed;
only the playbook's own managed Volta PATH block is replaced. A custom Fedora CLI
list must keep Zsh or ensure it already exists for the shell step.

[CI](../.github/workflows/validate.yml) lints both target trees and runs the
remaining regression tests. The [Fedora smoke test](../tests/fedora-smoke.sh)
selects DNF and verified release-RPM applications, leaves the full CLI/font lists in place, and
checks two runs plus installed tools/fonts and the user Flathub remote. It also
checks Node/npm in fresh login and interactive Zsh shells and the global `lts`
request. The previously linked CI run predates these mise checks. It does
not install Flatpak applications or launch GUIs. There is no macOS runtime job.
Thus verified Fedora native installation is not evidence of functional parity
for GUI apps, sandbox permissions, macOS packages, or login sessions.

Remaining review: full desktop validation on disposable Fedora/macOS targets.
The Proton Drive choice is resolved.

## ChatGPT Fedora bootstrap

The catalog selects `chatgpt` through DNF. Before broad package upgrades, a missing
ChatGPT package or missing pinned repository key triggers the
[bootstrap](../roles/fedora/tasks/bootstrap_chatgpt_payload.yml). Downloads and
verification run as the desktop user in a temporary directory. The
[verifier](../scripts/verify-chatgpt-rpm.sh) checks both SHA-256 hashes, the exact
public-key fingerprint and armored-key hash, then verifies the RPM signature in
an isolated RPM database and checks package name/version/architecture. Only then
are the verified key and RPM installed with sudo. DNF5 package signature checks
remain enabled; newer installed versions are not downgraded. Temporary downloads
and key databases are removed on success or failure. Existing installations with the pinned key present skip
the bootstrap download and continue through normal DNF updates.

Verified bootstrap inputs (2026-10-31, independently inspected on EVA without installation):

- [Official immutable RPM](https://persistent.oaistatic.com/codex-app-prod/linux/rpm/x86_64/chatgpt-26.1027.30824-1.x86_64.rpm):
  `chatgpt-26.1027.30824-1.x86_64`, 597768561 bytes;
  SHA-256 `c45045bef9cff939ff97797fb7b451ae7c5e499f321c02723d94395cf227dc86`.
- [Official public key bundle](https://persistent.oaistatic.com/codex-app-prod/linux/arch/26.1027.30824/repository-signing-key.gpg):
  SHA-256 `23e2cfbdef6afe95505f9e95a2cb63585da7ffe9b06a51ec08a32407c847d596`.
  The URL's `arch` component is OpenAI's key distribution path, not support for
  another workstation target in this playbook.
- RSA4096 fingerprint `3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4`, UID
  `Codex Linux Repository`, independently pinned in the
  [official installer source](https://persistent.oaistatic.com/codex-app-prod/linux/install-arch.sh)
  (read, never executed). Armored key SHA-256:
  `6c8933f828af390b2457f9e2d234082d783d6e4bb1911615b4861c6c61f4ea5a`.
- Inspected RPM scriptlets configure `openai-chatgpt`, base URL
  `https://persistent.oaistatic.com/codex-app-prod/linux/rpm/$basearch`, with
  `gpgcheck=1`, `repo_gpgcheck=1`, and the fingerprint-qualified armored key path
  under `/etc/pki/rpm-gpg`. Signed repository metadata and the recorded RPM digest
  were independently verified. Key rotation requires explicit review; failures
  do not silently disable checks or trust a replacement key.

The [implementation CI run](https://github.com/jmdarling/nervhq-playbook/actions/runs/41152587189)
at `638bf31f0c120f7189514c98169fd05110e16f6b` passed actual Fedora download,
verification and installation of `chatgpt-26.1027.30824-1.x86_64`, installed-file
verification (`rpm -V`), and a second run with `changed=0, failed=0`. Lint,
shell checks and all nine regression tests passed. Local tests use fake
verification tools to exercise rejection/order/cleanup contracts; the local
cloud proxy's download restriction did not prevent hosted CI validation.
GUI launch, login, Wayland behavior, user data, and macOS runtime remain untested.

## Dependency audit and first-run contract

No Arch/AUR support or AUR collections remain. `community.general` is still
required by user-scoped Flatpak operations on Fedora and Homebrew operations on
macOS. The full distro Ansible package includes it; a preflight check diagnoses
core-only or incomplete installs by checking the actual required modules before
loading roles. Workstation runs do not install or upgrade controller collections.
The optional developer setup also uses the full Ansible package, so neither
workflow downloads collections separately. Its Ansible 15 beta bundle is the
available full package compatible with the existing core 2.22 pin; the core
version remains stable and the Fedora system package is unchanged.

Native prerequisites have direct uses: curl downloads verified release archives;
tar + gzip extract mise/Starship; unzip extracts fonts; fontconfig rebuilds the
font cache; Flatpak manages user apps/remotes; gnupg2 verifies ChatGPT's signing
key. DNF's Python binding is installed through the CLI before invoking Ansible's
package module, so it is not a manual prerequisite. A curl-minimal provider is
accepted. Git is part of the Fedora CLI catalog instead of a hidden prerequisite.

`dnf5-plugins` was unused because COPR is configured by a repository file, and
`perl-Digest-SHA` is no longer needed because Fedora installers use the base
system's `sha256sum`. pip, a virtualenv and ansible-lint are development-only.
The platform/architecture and mutable-Fedora checks remain, but OS/Python/Ansible
version-number allowlists do not. CI releases are evidence of coverage, not a
version permission list; untested releases still depend on upstream packages.
