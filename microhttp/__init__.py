from nanohttp import configure, Controller
from microhttp import exceptions
from os.path import abspath, join, dirname


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


class Application:
    builtin_configuration = """
logging:
  version: 1
  disable_existing_loggers: false
  formatters:
    simple:
      format: "%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s"

  handlers:
    console:
      class: logging.StreamHandler
      formatter: simple
      level: DEBUG

  loggers:
    main:
      handlers:
      - console
      level: DEBUG    """

    def __init__(self, root: Controller, root_path: str='.'):
        self.root = root
        self.root_path = abspath(root_path)

    def configure(self, files=None, context=None, **kwargs):
        _context = {
            'root_path': self.root_path,
            'data_dir': join(self.root_path, 'data'),
            'microhttp_dir': abspath(dirname(__file__))
        }
        if context:
            _context.update(context)

        files = files or []
        configure(init_value=self.builtin_configuration, context=_context, files=files, **kwargs)
        from microhttp.ext import log
        log.configure()

    @classmethod
    def prepare(cls):
        pass

    def wsgi(self):
        return self.root.load_app()

bus = Bus().inner_bus
