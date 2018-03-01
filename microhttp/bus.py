

class BusInner:

    def __getattr__(self, item):
        x = BusInner()
        setattr(self, item, x)
        return x


class Bus(object):
    __slots__ = ('inner_bus', )

    def __init__(self):
        if not hasattr(self, 'inner_bus'):
            self.inner_bus = BusInner()


bus = Bus().inner_bus
