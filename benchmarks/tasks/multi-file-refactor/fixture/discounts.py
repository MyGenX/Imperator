def apply_discount(price, pct):
    """Return price after a percentage discount, rounded to whole cents."""
    discounted = price * (1 - pct / 100)
    return int(discounted * 100 + 0.5) / 100


def bulk_price(unit_price, qty, pct):
    """Discounted price for `qty` units."""
    return apply_discount(unit_price, pct) * qty
