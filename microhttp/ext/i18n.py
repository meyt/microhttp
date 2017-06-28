"""
    Internationalization Extension
    
    Usage:
    Config: YAML 
        i18n:
          locales:
            - en_US
            - fa_IR
          localedir: myapp/i18n
          domain: app
          default: fa_IR
          
    Change locale:
        >>> set_locale('en_US')
    
    Translate :
        >>> _('HelloWorld')
    
"""

from nanohttp import settings
from microhttp import bus
from microhttp.ext import log
import gettext
import locale as lib_locale


def configure():
    bus.ext.i18n.locales_translation = {}
    # load translations
    for locale in settings.i18n.locales:
        bus.ext.i18n.locales_translation[locale] = gettext.translation(
            domain=settings.i18n.domain,
            localedir=settings.i18n.localedir,
            languages=[locale]
        )
    # Set default Locale
    set_locale(settings.i18n.default)


def get_default() -> str:
    return bus.ext.i18n.default


def set_locale(locale=None):
    bus.ext.i18n.default = locale
    try:
        lib_locale.setlocale(lib_locale.LC_ALL, bus.ext.i18n.default)
    except lib_locale.Error:
        log.exception('microhttp.ext.i18n: Locale error (%s)' % bus.ext.i18n.default)


def translate(word, plural=None) -> str:
    if bus.ext.i18n.default in bus.ext.i18n.locales_translation:
        if plural is not None:
            return bus.ext.i18n.locales_translation[bus.ext.i18n.default].ngettext(word, plural)
        else:
            return bus.ext.i18n.locales_translation[bus.ext.i18n.default].gettext(word)
    else:
        return word
_ = translate
