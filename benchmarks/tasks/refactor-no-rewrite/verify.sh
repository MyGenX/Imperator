#!/usr/bin/env bash
set -e
python3 - <<'PY'
from formatter import label, shout
# behavior must be preserved
assert label("open") == "Open"
assert label("closed") == "Closed"
assert label("pending") == "Pending"
assert label("whatever") == "Unknown"
assert shout("hi") == "HI!"   # unrelated function must still work

# the requested transformation must actually have happened
src = open("formatter.py").read()
assert "elif" not in src, "label() still uses an if/elif chain; expected a dict lookup"
print("ok")
PY
