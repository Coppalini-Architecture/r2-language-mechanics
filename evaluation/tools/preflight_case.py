#!/usr/bin/env python3
"""Validate an AEC-1 case carrier without executing its extension.

Usage: python3 -I preflight_case.py CASE.json
Exit 0 for an admitted carrier; exit 2 for REJECT.
"""
import json
import re
import sys
from pathlib import Path

REQUIRED = (
    "eval_id", "base_commit", "target", "claim", "domain", "predicate",
    "extension_sha256", "readers", "bounds", "commands",
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def reject(reason: str) -> None:
    print(f"PREFLIGHT REJECT {reason}")
    raise SystemExit(2)


if len(sys.argv) != 2:
    reject("usage")
try:
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
except Exception as exc:
    reject(f"json {type(exc).__name__}")
missing = [field for field in REQUIRED if field not in data]
if missing:
    reject("missing " + ",".join(missing))
if not re.fullmatch(r"EVAL-\d{4}", str(data["eval_id"])):
    reject("eval_id")
if not COMMIT.fullmatch(str(data["base_commit"])):
    reject("base_commit")
if data["claim"] not in ("exact", "construction", "open"):
    reject("claim")
if not isinstance(data["target"], dict) or not data["target"].get("invariant"):
    reject("target")
if not isinstance(data["domain"], dict) or not data["domain"].get("bound"):
    reject("domain")
if not isinstance(data["predicate"], dict) or not data["predicate"].get("command"):
    reject("predicate")
if not SHA256.fullmatch(str(data["extension_sha256"])):
    reject("extension_sha256")
if not isinstance(data["readers"], list) or not data["readers"]:
    reject("readers")
if not isinstance(data["bounds"], dict) or not all(
    name in data["bounds"] for name in (
        "cpu_seconds", "memory_mib", "wall_seconds", "output_bytes",
        "fixture_bytes", "processes",
    )
):
    reject("bounds")
if not isinstance(data["commands"], dict) or not all(
    name in data["commands"] for name in ("build", "run", "replay", "receipt")
):
    reject("commands")
print("PREFLIGHT PASS", data["eval_id"], data["claim"], data["target"]["invariant"])
