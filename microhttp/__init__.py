from nanohttp import configure, Controller
from os.path import abspath
from microhttp import exceptions
import threading


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


class Bus:

    def get_current(self):
        if not hasattr(self.thread_local, 'colony_bus'):
            raise exceptions.BusNotInitializedException('Bus not initialized')
        else:
            return self.thread_local.colony_bus

    def __init__(self):
        self.thread_local = threading.local()
        if not hasattr(self.thread_local, 'colony_bus'):
            self.thread_local.colony_bus = BusInner()

    def __getattr__(self, key):
        return getattr(self.thread_local.colony_bus, key)

    def __setattr__(self, key, value):
        setattr(self.thread_local.colony_bus, key, value)

    def __delattr__(self, key):
        delattr(self.thread_local.colony_bus, key)


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

    def __init__(self, name: str, root: Controller, root_path='.', version='0.1.0-dev.0', process_name=None):
        self.process_name = process_name or name
        self.version = version
        self.name = name
        self.root = root
        self.root_path = abspath(root_path)

    def configure(self, files=None, context=None, **kwargs):
        _context = {
            'process_name': self.process_name,
            'root_path': self.root_path,
        }
        if context:
            _context.update(context)

        files = files or []
        configure(init_value=self.builtin_configuration, files=files, context=_context, **kwargs)
        from microhttp.ext import log
        log.configure()

    # noinspection PyMethodMayBeStatic
    def register_cli_launchers(self, subparsers):
        """
        This is a template method
        """
        pass

    @classmethod
    def prepare(cls):
        pass

    def wsgi(self):
        return self.root.load_app()

bus = Bus()
