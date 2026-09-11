#!/usr/bin/env python3
"""Structural validation for the templates catalog (audit useteploy__templates-03).

Checks index.json against the template files it points at, so catalog
drift fails in this repository instead of at a user's install:

- index.json is valid JSON, a non-empty list, with unique names
- every entry has a <name>/teploy.yml
- every {{placeholder}} used in a template is declared in the index
  (an undeclared variable makes `teploy template install` fail at
  fetch time with a missing-variable error)
- every declared variable is actually used
- every accessory named in the index exists in the template
- "generate" sentinels only appear in env-value position

The full render-and-parse check against the real Teploy parser runs in
CI via teploy-cli's TestRenderAllCatalogTemplates (see
.github/workflows/validate.yml).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
SENTINEL = re.compile(r":\s*(\"generate\"|generate)\s*$")

errors = []


def fail(msg):
    errors.append(msg)


index_raw = (ROOT / "index.json").read_text(encoding="utf-8")
try:
    index = json.loads(index_raw)
except json.JSONDecodeError as e:
    sys.exit(f"index.json is not valid JSON: {e}")

if not isinstance(index, list) or not index:
    sys.exit("index.json must be a non-empty list")

seen = set()
for entry in index:
    name = entry.get("name", "")
    if not name:
        fail("index entry without a name")
        continue
    if name in seen:
        fail(f"duplicate catalog entry: {name}")
    seen.add(name)

    tpl_path = ROOT / name / "teploy.yml"
    if not tpl_path.is_file():
        fail(f"{name}: no teploy.yml at {tpl_path.relative_to(ROOT)}")
        continue
    tpl = tpl_path.read_text(encoding="utf-8")

    used = set(PLACEHOLDER.findall(tpl))
    declared = set(entry.get("variables") or [])

    undeclared = sorted(used - declared)
    if undeclared:
        fail(f"{name}: template uses variables not declared in index.json: {undeclared}")
    unused = sorted(declared - used)
    if unused:
        fail(f"{name}: index.json declares variables the template never uses: {unused}")

    # The index's "accessories" mix two conventions across the catalog:
    # image kinds (postgres, valkey, machine-learning) and accessory keys
    # (lullmail's "db"). Accept a match against either the keys defined
    # under accessories: or the image references in the file.
    keys = set(re.findall(r"^\s{2}([A-Za-z0-9][A-Za-z0-9_-]*):\s*$", tpl, re.M))
    image_names = []
    for image in re.findall(r"^\s*image:\s*(\S+)", tpl, re.M):
        repo = image.split("@")[0]
        if ":" in repo.rsplit("/", 1)[-1]:
            repo = repo.rsplit(":", 1)[0] if "/" in repo else repo.split(":")[0]
        image_names.append(repo.rsplit("/", 1)[-1])

    def accessory_matches(acc):
        if acc in keys:
            return True
        return any(acc == n or acc in n for n in image_names)

    for acc in entry.get("accessories") or []:
        if not accessory_matches(acc):
            fail(f"{name}: index lists accessory {acc!r} but the template defines neither "
                 f"such a key nor a matching image (keys: {sorted(keys)}, images: {image_names})")

    for i, line in enumerate(tpl.splitlines(), 1):
        if SENTINEL.search(line) and not re.match(r"^\s*[A-Za-z0-9_.-]+:\s", line):
            fail(f"{name}:{i}: 'generate' sentinel outside an env-value position: {line.strip()!r}")

# Directories with a teploy.yml that the index forgot.
cataloged = {e.get("name") for e in index if e.get("name")}
for d in sorted(ROOT.iterdir()):
    if d.is_dir() and not d.name.startswith(".") and (d / "teploy.yml").is_file():
        if d.name not in cataloged:
            fail(f"{d.name}: template directory exists but is not in index.json")

if errors:
    print("catalog validation failed:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"catalog ok: {len(index)} templates validated")
