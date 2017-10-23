from nanohttp import configure, Controller, Application as NanohttpApplication
from os.path import abspath, join, dirname


class Application(NanohttpApplication):
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

    def __init__(self, root: Controller=None, root_path: str='.'):
        super(Application, self).__init__(root=root)
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
