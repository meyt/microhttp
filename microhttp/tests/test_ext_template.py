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

            @template.render('have_issues.mako')
            def have_issues(self):
                template.set_template('test_dir2')
                return {'today': date.today()}

            @template.render('have_issues2.mako')
            def missed_file(self):
                template.set_template('test_dir2')
                return {'today': date.today()}

            @template.render('advanced.mako')
            def invalid_data(self):
                template.set_template('test_dir2')
                return 'success'

            @template.render('advanced.mako')
            def auto_to_dict(self):
                template.set_template('test_dir2')

                class Dummy:
                    @staticmethod
                    def to_dict():
                        return {}

                return Dummy

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
        self.app.get('/simple', status=200)

    def test_unicode(self):
        resp = self.app.get('/unicode')
        self.assertEqual(resp.text, (
            'Hallo wêreld, Здравей, свят, 世界您好, Ahoj světe, Γεια σου κόσμε, שלום לך עולם, '
            'हैलो वर्ल्डm ハローワールド,  , หวัดดีชาวโลก, Привіт, народ, سلام دنيا, Chào thế giới'
        ))

    def test_advanced(self):
        resp = self.app.get('/advanced')
        self.assertEqual(resp.text, '<span>today: %s</span>' % date.today())

    def test_auto_to_dict(self):
        self.app.get('/auto_to_dict')

    def test_error_handling(self):
        self.app.get('/have_issues')

        settings.debug = False
        self.app.get('/have_issues', status=500)
        settings.debug = True

        self.app.get('/missed_file', status=500)

        self.app.get('/invalid_data', status=500)


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
