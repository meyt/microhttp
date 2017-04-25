import unittest
from nanohttp import Controller
from microhttp import Application as BaseApplication
from microhttp.ext import template
from microhttp.tests.helpers import WebTestCase
from datetime import date


class TestCase(WebTestCase):

    class Application(BaseApplication):
        class Root(Controller):
            @template.render
            def simple(self):
                template.set_template('test_dir1')
                return 'simple.mako', dict()

            @template.render
            def unicode(self):
                template.set_template('test_dir2')
                return 'unicode.mako', dict()

            @template.render
            def advanced(self):
                template.set_template('test_dir2')
                return 'advanced.mako', {'today': date.today()}

        def __init__(self):
            self.builtin_configuration += """

template:
  test_dir1:
    directories:
      - %(microhttp_dir)s/tests/stuff/template_dir1
  test_dir2:
    directories:
      - %(microhttp_dir)s/tests/stuff/template_dir2
            """
            super().__init__(self.Root())

        def prepare(self):
            template.configure()

    def test_simple(self):
        resp = self.app.get('/simple')
        assert resp.status_int == 200

    def test_unicode(self):
        resp = self.app.get('/unicode')
        assert resp.text == (
            'Hallo wêreld, Здравей, свят, 世界您好, Ahoj světe, Γεια σου κόσμε, שלום לך עולם, '
            'हैलो वर्ल्डm ハローワールド,  , หวัดดีชาวโลก, Привіт, народ, سلام دنيا, Chào thế giới'
        )

    def test_advanced(self):
        resp = self.app.get('/advanced')
        assert resp.text == '<span>today: %s</span>' % date.today()

if __name__ == '__main__':
    unittest.main()
