from os.path import abspath, join, dirname
from nanohttp import (
    configure,
    Controller,
    Application as NanohttpApplication,
    HttpInternalServerError,
    HttpStatus
)
from microhttp.exceptions import SqlError
from sqlalchemy.exc import SQLAlchemyError


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
        self.after_load_configuration()
        from microhttp.ext import log
        log.configure()

    # noinspection PyMethodMayBeStatic
    def after_load_configuration(self):  # pragma: nocover
        """ A hook called after configurations load """
        pass

    @classmethod
    def prepare(cls):  # pragma: nocover
        """ Reserved for preparing the application """
        raise NotImplementedError

    def _handle_exception(self, ex):
        from microhttp.ext import log
        if isinstance(ex, SQLAlchemyError):
            ex = SqlError(ex)
            log.exception(str(ex))
        if not isinstance(ex, HttpStatus):
            ex = HttpInternalServerError('Internal server error')
            log.exception('Internal server error')
        return super()._handle_exception(ex)
