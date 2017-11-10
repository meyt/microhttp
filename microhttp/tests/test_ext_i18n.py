import unittest
from nanohttp import Controller, html, settings
from microhttp import Application as BaseApplication
from microhttp.ext import i18n
from microhttp.tests.helpers import WebTestCase
from locale import Error as LocaleError


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self, locale: str='en_us'):
                _ = i18n.translate
                i18n.set_locale(locale)
                return _('Hello World')

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)
            settings.merge("""
                i18n:
                  locales:
                    - en_US
                    - fa_IR
                  localedir: %(microhttp_dir)s/tests/stuff/i18n
                  domain: microhttp_app
                  default: en_us
            """)
            try:
                i18n.configure()
            except LocaleError:
                pass

    def test_default(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.text, 'Hello World')

    def test_en_us(self):
        resp = self.app.get('/en_US')
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.text, 'Hello World')

    def test_fa_ir(self):
        resp = self.app.get('/fa_IR')
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.text, 'سلام دنیا')

if __name__ == '__main__':  # pragma: nocover
    unittest.main()
