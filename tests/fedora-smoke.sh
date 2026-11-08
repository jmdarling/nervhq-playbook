#!/bin/bash
# Run only inside the disposable Fedora container specified by CI.
set -euo pipefail
[[ $(id -u) == 0 && ( -f /run/.containerenv || -f /.dockerenv ) ]] || { echo 'Disposable root Fedora container required' >&2; exit 1; }
# The only playbook prerequisite is distro Ansible. sudo and the test user
# emulate a normal Workstation installation; do not preinstall pip, Git or
# Python development tooling, and do not run scripts/bootstrap.sh.
dnf5 install -y ansible sudo
useradd --create-home tester
printf 'tester ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/tester
chmod 440 /etc/sudoers.d/tester
cp -a /source /home/tester/playbook
chown -R tester:tester /home/tester/playbook
sudo -H -u tester bash <<'USER'
set -euo pipefail
cd /home/tester/playbook
python3 --version
ansible --version
test ! -d .venv
# Exercise all configured native Fedora packages (including COPR/vendor packages),
# user installers/fonts, and user Flathub configuration. Flatpak application
# installation/GUI launches need a real desktop session and are excluded here.
python - <<'PYVARS'
from pathlib import Path
import yaml
catalog = yaml.safe_load(Path('inventory/group_vars/all/applications.yml').read_text())
applications = [item for item in catalog['applications']
                if item.get('fedora', {}).get('source') in ['dnf', 'release_rpm']]
Path('/tmp/smoke-vars.yml').write_text(yaml.safe_dump({'applications': applications}))
PYVARS
ansible-playbook local-fedora.yml -e @/tmp/smoke-vars.yml
ansible-playbook local-fedora.yml -e @/tmp/smoke-vars.yml | tee /tmp/second-run.log
grep -Eq 'changed=0[[:space:]]' /tmp/second-run.log
"$HOME/.local/bin/mise" --version
# Read the managed login profile and interactive setup from a clean PATH.
env PATH=/usr/bin:/bin zsh -lc 'command -v mise node npm npx && node --version && npm --version && npx --version'
env PATH=/usr/bin:/bin zsh -ic 'command -v mise node npm npx && node --version && npm --version && npx --version'
test "$("$HOME/.local/bin/mise" config get --global tools.node)" = lts
"$HOME/.local/bin/starship" --version
# CLI checks only: do not create containers, machines, sockets or user namespaces.
git --version
podman --version
podman --help >/dev/null
rpm -q chatgpt
rpm -V chatgpt
fc-list | grep 'FiraCode'
flatpak remotes --user | grep flathub
USER
