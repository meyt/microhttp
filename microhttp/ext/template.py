from mako.lookup import TemplateLookup
from mako import exceptions
from nanohttp import html, settings, InternalServerError
from microhttp import bus
from microhttp.ext import log
import functools


def configure():
    bus.ext.template = Template()


class Template:
    _lookup = None

    def set_template(self, template_name: str):
        template_args = {'input_encoding': 'utf8'}
        template_args.update(settings.template[template_name])
        self._lookup = TemplateLookup(**template_args)

    def render(self, filename: str, data: dict):
        # noinspection PyBroadException
        try:
            return self._lookup.get_template(filename).render(**data)
        except Exception:
            if settings.debug:
                # noinspection PyBroadException
                try:
                    return exceptions.html_error_template().render().decode('utf-8')
                except Exception:
                    log.exception('Template render exception - Debug Mode')
                    return 'Cannot locate template file (%s).' % filename
            else:
                log.exception('Template render exception')
                import sys
                raise InternalServerError(sys.exc_info())


def set_template(template_name):
    bus.ext.template.set_template(template_name)


def _render(func):
    """
    Mako Decorator
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        filename, result = func(*args, **kwargs)
        return bus.ext.template.render(filename=filename, data=result)
    return wrapper


render = functools.partial(html, inner_decorator=_render)
