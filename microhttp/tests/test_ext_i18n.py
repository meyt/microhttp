import unittest
from nanohttp import Controller, html, settings
from microhttp import Application as BaseApplication
from microhttp.ext import i18n
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self, locale: str=None):
                locale = locale or i18n.get_default()
                _ = i18n.translate
                i18n.set_locale(locale)
                return _('Hello World')

            @html
            def plural(self, locale: str=None, count: int=0):
                locale = locale or i18n.get_default()
                _ = i18n.translate
                i18n.set_locale(locale)
                return _('One new notification', '%(count)d new notification', int(count)) % {'count': int(count)}

        def __init__(self):
            super().__init__(self.Root())

        @staticmethod
        def begin_request():
            i18n.set_locale_from_request(('fa-ir', 'en-us'))

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
            i18n.configure()

    def test_default(self):
        resp = self.app.get('/', status=200)
        self.assertEqual(resp.text, 'Hello World')

        # If default locale not exist in defined locales
        resp = self.app.get('/rr_rr', status=200)
        self.assertEqual(resp.text, 'Hello World')

    def test_en_us(self):
        resp = self.app.get('/en_US', status=200)
        self.assertEqual(resp.text, 'Hello World')

    def test_fa_ir(self):
        resp = self.app.get('/fa_IR', status=200)
        self.assertEqual(resp.text, 'سلام دنیا')

        resp = self.app.get('/plural/fa_IR/1', status=200)
        self.assertEqual(resp.text, 'یک اعلان جدید')

        resp = self.app.get('/plural/fa_IR/2', status=200)
        self.assertEqual(resp.text, '2 اعلان جدید')

        resp = self.app.get('/plural/fa_IR/5', status=200)
        self.assertEqual(resp.text, 'اعلانات: 5')

    def test_by_request(self):
        # Set valid language in request header
        resp = self.app.get('/', headers={
            'accept-language': 'fa-ir'
        }, status=200)
        self.assertEqual(resp.text, 'سلام دنیا')

        # Invalid locale, use default locale
        resp = self.app.get('/', headers={
            'accept-language': 'rr-rr'
        }, status=200)
        self.assertEqual(resp.text, 'Hello World')


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
