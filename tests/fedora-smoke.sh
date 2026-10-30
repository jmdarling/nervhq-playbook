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
# Exercise real DNF5/bootstrap, user Flatpak remote, shell, pinned user installers
# and font extraction. GUI apps/COPR are intentionally outside this smoke test.
cat > /tmp/smoke-vars.yml <<'VARS'
applications: []
cli_tools:
  - name: zsh
    fedora:
      source: dnf
  - name: fzf
    fedora:
      source: dnf
  - name: volta
    fedora:
      source: script
      script_name: install-volta.sh
      creates: "{{ ansible_facts.env.HOME }}/.volta/bin/volta"
  - name: starship
    fedora:
      source: script
      script_name: install-starship.sh
      creates: "{{ ansible_facts.env.HOME }}/.local/bin/starship"
VARS
ansible-playbook local-fedora.yml -e @/tmp/smoke-vars.yml
ansible-playbook local-fedora.yml -e @/tmp/smoke-vars.yml | tee /tmp/second-run.log
grep -Eq 'changed=0[[:space:]]' /tmp/second-run.log
"$HOME/.volta/bin/volta" --version
"$HOME/.local/bin/starship" --version
fc-list | grep 'FiraCode'
flatpak remotes --user | grep flathub
USER
