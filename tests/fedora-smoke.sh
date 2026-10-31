#!/bin/bash
# Run only inside the disposable Fedora container specified by CI.
set -euo pipefail
[[ $(id -u) == 0 && ( -f /run/.containerenv || -f /.dockerenv ) ]] || { echo 'Disposable root Fedora container required' >&2; exit 1; }
dnf5 install -y python3 python3-pip sudo git
useradd --create-home tester
printf 'tester ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/tester
chmod 440 /etc/sudoers.d/tester
cp -a /source /home/tester/playbook
chown -R tester:tester /home/tester/playbook
sudo -H -u tester bash <<'USER'
set -euo pipefail
cd /home/tester/playbook
python3 --version
PYTHON=python3 bash scripts/bootstrap.sh
export PATH="$PWD/.venv/bin:$PATH"
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
"$HOME/.volta/bin/volta" --version
"$HOME/.local/bin/starship" --version
# CLI checks only: do not create containers, machines, sockets or user namespaces.
podman --version
podman --help >/dev/null
rpm -q chatgpt
rpm -V chatgpt
fc-list | grep 'FiraCode'
flatpak remotes --user | grep flathub
USER
