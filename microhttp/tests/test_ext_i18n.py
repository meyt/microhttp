import unittest
from nanohttp import Controller, html
from microhttp import Application as BaseApplication
from microhttp.ext import i18n
from microhttp.tests.helpers import WebTestCase
from locale import Error as LocaleError


class TestCase(WebTestCase):

    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self):
                _ = i18n.translate
                return _('Hello World')

            @html
            def fa_ir(self):
                _ = i18n.translate
                try:
                    i18n.set_locale('fa_IR')
                except LocaleError:
                    pass
                return _('Hello World')

            @html
            def en_us(self):
                _ = i18n.translate
                try:
                    i18n.set_locale('en_US')
                except LocaleError:
                    pass
                return _('Hello World')

        def __init__(self):
            self.builtin_configuration += """

i18n:
  locales:
    - en_US
    - fa_IR
  localedir: %(microhttp_dir)s/tests/stuff/i18n
  domain: microhttp_app
  default: en_US
  """
            super().__init__(self.Root())

        def prepare(self):
            try:
                i18n.configure()
            except LocaleError:
                pass

    def test_default(self):
        resp = self.app.get('/')
        assert resp.status_int == 200
        assert resp.text == 'Hello World'

    def test_en_us(self):
        resp = self.app.get('/en_us')
        assert resp.status_int == 200
        assert resp.text == 'Hello World'

    def test_fa_ir(self):
        resp = self.app.get('/fa_ir')
        assert resp.status_int == 200
        assert resp.text == 'سلام دنیا'


if __name__ == '__main__':
    unittest.main()
