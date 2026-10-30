"""Exercise installer failures using fake commands; never install host software."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALLERS = list(ROOT.glob("roles/*/files/install-volta.sh")) + [
    ROOT / "roles/fedora/files/install-starship.sh",
    ROOT / "roles/fedora/files/install-fira-code-nerd-font.sh",
]


class InstallerFailures(unittest.TestCase):
    def test_failed_download_is_not_executed_and_temp_file_is_removed(self):
        for script in INSTALLERS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                bin_dir = root / "bin"
                bin_dir.mkdir()
                home = root / "home"
                home.mkdir()
                # Simulate a server returning executable content and a failed download.
                curl = bin_dir / "curl"
                curl.write_text("#!/bin/bash\nwhile [ $# -gt 0 ]; do\n"
                                "  if [ \"$1\" = -o ]; then shift; out=$1; fi\n"
                                "  shift\ndone\n"
                                "if [ -n \"${out:-}\" ]; then\n"
                                "  printf 'touch \"$MARKER\"\\n' > \"$out\"\n"
                                "else\n  printf 'touch \"$MARKER\"\\n'\nfi\nexit 22\n")
                curl.chmod(0o755)
                env = dict(os.environ, PATH=str(bin_dir) + ":" + os.environ["PATH"],
                           HOME=str(home), TMPDIR=tmp, MARKER=str(root / "executed"))
                result = subprocess.run(["bash", str(script)], env=env,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 22, result.stderr)
                self.assertFalse((root / "executed").exists())
                self.assertEqual(sorted(p.name for p in root.iterdir()), ["bin", "home"])


if __name__ == "__main__":
    unittest.main()
