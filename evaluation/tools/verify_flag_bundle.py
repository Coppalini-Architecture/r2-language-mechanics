#!/usr/bin/env python3
"""Check the required carrier of an AEC-1 flag bundle.

Usage: python3 -I verify_flag_bundle.py FLAGS/F-<eval-id>
This checker validates the bundle shape and manifest only. Its output is an
adjudication input; semantic confirmation remains the declared verifier's job.
"""
import hashlib
import sys
from pathlib import Path

REQUIRED = (
    "FLAG.md", "base.lock", "commands.txt", "run-primary-1.txt",
    "run-primary-2.txt", "run-independent.txt", "reduce.log",
    "MANIFEST.sha256",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if len(sys.argv) != 2:
    print("FLAG REJECT usage")
    raise SystemExit(2)
root = Path(sys.argv[1])
missing = [name for name in REQUIRED if not (root / name).is_file()]
if not (root / "witness").is_dir():
    missing.append("witness/")
if not (root / "certificate").is_dir():
    missing.append("certificate/")
if missing:
    print("FLAG REJECT missing " + ",".join(missing))
    raise SystemExit(2)
bad = []
for line in (root / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    try:
        wanted, rel = line.split(maxsplit=1)
    except ValueError:
        bad.append("manifest-format")
        continue
    path = root / rel.strip().removeprefix("*")
    if not path.is_file() or digest(path) != wanted:
        bad.append(rel)
if bad:
    print("FLAG REJECT manifest " + ",".join(bad))
    raise SystemExit(2)
print("FLAG CARRIER PASS", root.name)
