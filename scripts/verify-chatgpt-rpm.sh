#!/bin/bash
# Read/verify only. Never run package scriptlets or import into the system RPM DB.
set -euo pipefail
work_dir=$1
fingerprint=3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4
cd "$work_dir"
printf '%s  %s\n' \
  c45045bef9cff939ff97797fb7b451ae7c5e499f321c02723d94395cf227dc86 package.rpm \
  23e2cfbdef6afe95505f9e95a2cb63585da7ffe9b06a51ec08a32407c847d596 key.gpg | sha256sum --check --strict
mkdir -m 700 gnupg rpmdb
export GNUPGHOME="$work_dir/gnupg"
gpg --batch --import key.gpg
actual=$(gpg --batch --with-colons --fingerprint | awk -F: '$1 == "fpr" {print $10}')
[ "$actual" = "$fingerprint" ] || { echo 'Unexpected OpenAI signing key' >&2; exit 1; }
gpg --batch --armor --export "$fingerprint" > key.asc
printf '%s  %s\n' 6c8933f828af390b2457f9e2d234082d783d6e4bb1911615b4861c6c61f4ea5a key.asc | sha256sum --check --strict
rpm --dbpath "$work_dir/rpmdb" --initdb
rpm --dbpath "$work_dir/rpmdb" --import "$work_dir/key.asc"
rpmkeys --dbpath "$work_dir/rpmdb" --checksig "$work_dir/package.rpm"
identity=$(rpm --dbpath "$work_dir/rpmdb" -qp --queryformat '%{NAME} %{VERSION}-%{RELEASE} %{ARCH}' "$work_dir/package.rpm")
[ "$identity" = 'chatgpt 26.1027.30824-1 x86_64' ] || { echo 'Unexpected ChatGPT package identity' >&2; exit 1; }
