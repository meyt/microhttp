import unittest
from nanohttp import Controller, settings
from microhttp import Application as BaseApplication
from microhttp.ext import template
from microhttp.tests.helpers import WebTestCase
from datetime import date


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @template.render('simple.mako')
            def simple(self):
                template.set_template('test_dir1')
                return dict()

            @template.render('unicode.mako')
            def unicode(self):
                template.set_template('test_dir2')
                return dict()

            @template.render('advanced.mako')
            def advanced(self):
                template.set_template('test_dir2')
                return {'today': date.today()}

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)
            settings.merge("""
                template:
                  test_dir1:
                    directories:
                      - %(microhttp_dir)s/tests/stuff/template_dir1
                  test_dir2:
                    directories:
                      - %(microhttp_dir)s/tests/stuff/template_dir2
            """)
            template.configure()

    def test_simple(self):
        resp = self.app.get('/simple')
        self.assertEqual(resp.status_int, 200)

    def test_unicode(self):
        resp = self.app.get('/unicode')
        self.assertEqual(resp.text, (
            'Hallo wêreld, Здравей, свят, 世界您好, Ahoj světe, Γεια σου κόσμε, שלום לך עולם, '
            'हैलो वर्ल्डm ハローワールド,  , หวัดดีชาวโลก, Привіт, народ, سلام دنيا, Chào thế giới'
        ))

    def test_advanced(self):
        resp = self.app.get('/advanced')
        self.assertEqual(resp.text, '<span>today: %s</span>' % date.today())

if __name__ == '__main__':  # pragma: nocover
    unittest.main()
