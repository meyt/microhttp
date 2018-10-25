
from os.path import abspath, join, dirname

from sqlalchemy.exc import SQLAlchemyError

from nanohttp import (
    configure,
    settings,
    Controller,
    Application as NanohttpApplication,
    HTTPInternalServerError,
    HTTPStatus
)

from microhttp.exceptions import SqlError


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
    microhttp:
      handlers:
      - console
      level: DEBUG
      
    main:
      handlers:
      - console
      level: DEBUG    """

    def __init__(self, root: Controller=None, root_path: str='.'):
        super(Application, self).__init__(root=root)
        self.root_path = abspath(root_path)

    def configure(self, files=None, force=False, context=None, **kwargs):
        _context = {
            'root_path': self.root_path,
            'data_dir': join(self.root_path, 'data'),
            'microhttp_dir': abspath(dirname(__file__))
        }
        if context:
            _context.update(context)

        files = files or []
        configure(
            context=_context,
            force=force,
            **kwargs
        )
        settings.merge(self.builtin_configuration)

        if files:
            for f in files:
                settings.load_file(f)

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

    def _handle_exception(self, ex, start_response):
        from microhttp.ext import log
        if isinstance(ex, SQLAlchemyError):
            ex = SqlError(ex)
            log.exception(str(ex))
        if not isinstance(ex, HTTPStatus):
            ex = HTTPInternalServerError('Internal server error')
            log.exception('Internal server error')
        return super()._handle_exception(ex, start_response)
