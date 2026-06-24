_items = {}


def add_item(name, qty):
    _items[name] = _items.get(name, 0) + qty
    return _items[name]


def get_item(name):
    return _items.get(name, 0)
