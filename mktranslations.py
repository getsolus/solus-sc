#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

# Enable verbose output
def run(cmd):
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

# Create po directory if it doesn't exist
po_dir = Path("po")
po_dir.mkdir(exist_ok=True)

# Collect Python source files with gettext calls
py_files = set()
for ext in ['_("', "_('"]:
    result = subprocess.run(
        ["grep", "-rl", ext, "."],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    for line in result.stdout.strip().splitlines():
        if line.endswith(".py"):
            py_files.add(line)

# Write POTFILES.in
with open(po_dir / "POTFILES.in", "w", encoding="utf-8") as pot:
    for f in py_files:
        pot.write(f + "\n")
print(f"+ Wrote {po_dir / 'POTFILES.in'}")

# Extract messages to solus-sc.pot
run([
    "pybabel", "extract",
    "-F", "babel.cfg",  # Optional config
    "-o", "po/solus-sc.pot",
    "."
])


