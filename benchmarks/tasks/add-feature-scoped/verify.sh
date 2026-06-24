#!/usr/bin/env bash
set -e
python3 - <<'PY'
import inventory
inventory.add_item("a", 3)
assert inventory.get_item("a") == 3
assert inventory.remove_item("a") is True
assert inventory.get_item("a") == 0
assert inventory.remove_item("missing") is False
print("ok")
PY
