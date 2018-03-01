from mako.lookup import TemplateLookup
from mako import exceptions
from nanohttp import action, settings, HttpInternalServerError
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
                    raise HttpInternalServerError('Cannot locate template file (%s).' % filename)
            else:
                log.exception('Template render exception')
                import sys
                raise HttpInternalServerError(sys.exc_info())


def set_template(template_name):
    bus.ext.template.set_template(template_name)


def _render(func, filename):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)
        if hasattr(result, 'to_dict'):
            result = result.to_dict()
        elif not isinstance(result, dict):
            raise ValueError('The result must be an instance of dict, not: %s' % type(result))

        return bus.ext.template.render(filename, result)

    return wrapper


render = functools.partial(action, content_type='text/html', inner_decorator=_render)
