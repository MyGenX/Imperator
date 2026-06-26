#!/usr/bin/env bash
set -e
python3 - <<'PY'
from discounts import apply_discount, bulk_price
from invoices import line_total, invoice_total

# behavior must be preserved exactly
assert apply_discount(100, 10) == 90.0
assert apply_discount(9.99, 15) == 8.49
assert bulk_price(10, 2, 2) == 19.6
assert line_total(2.5, 3) == 7.5
assert line_total(0.1, 3) == 0.3
assert invoice_total([(2.5, 3), (0.1, 3)]) == 7.8

# the requested extraction must actually have happened
from money import round_cents
assert round_cents(8.4915) == 8.49
assert round_cents(7.5) == 7.5

import re
for mod in ("discounts.py", "invoices.py"):
    src = open(mod).read()
    assert "round_cents" in src, f"{mod} should call the new round_cents helper"
    assert "* 100 + 0.5" not in src, f"{mod} still inlines the rounding expression"
print("ok")
PY
