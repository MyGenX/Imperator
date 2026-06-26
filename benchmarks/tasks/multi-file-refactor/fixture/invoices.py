def line_total(unit_price, qty):
    """Total for one invoice line, rounded to whole cents."""
    total = unit_price * qty
    return int(total * 100 + 0.5) / 100


def invoice_total(lines):
    """Sum of line totals. `lines` is a list of (unit_price, qty) tuples."""
    return sum(line_total(price, qty) for price, qty in lines)
