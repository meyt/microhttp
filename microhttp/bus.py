

class BusInner:
    _items = {}

    def __getattr__(self, item):
        x = BusInner()
        setattr(self, item, x)
        return x

    def __setitem__(self, key, value):
        self._items[key] = value

    def __getitem__(self, item):
        return self._items[item]

    def __delitem__(self, key):
        del self._items[key]

    def __contains__(self, item):
        return item in self._items


class Bus(object):
    __slots__ = ('inner_bus', )

    def __init__(self):
        if not hasattr(self, 'inner_bus'):
            self.inner_bus = BusInner()

bus = Bus().inner_bus
