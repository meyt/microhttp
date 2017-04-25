import unittest
from nanohttp import Controller, html
from microhttp import Application as BaseApplication
from microhttp.ext import session
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    class Application(BaseApplication):
        class Root(Controller):

            @html
            def init_counter(self):
                with session.get_session() as s:
                    s['counts'] = 0

                return ''

            @html
            def inc_count(self):
                with session.get_session() as s:
                    s['counts'] += 1
                    counts = s['counts']
                return str(counts)

        def __init__(self):
            self.builtin_configuration += """

session:
  dogpile:  
    backend: dogpile.cache.dbm
    expiration_time: 3600
    arguments:
      filename:  %(microhttp_dir)s/tests/stuff/sessions.dbm
  cookie_name: x_session
"""
            super().__init__(self.Root())

        def prepare(self):
            session.configure()

    def test_simple(self):
        resp = self.app.get('/init_counter')
        assert resp.status_int == 200
        assert 'x_session' in self.app.cookies
        for x in range(1, 10):
            resp = resp.goto('/inc_count')
            assert resp.status_int == 200
            assert resp.text == str(x)

    def test_advanced(self):
        for _ in range(20):
            self.setUp()
            resp = self.app.get('/init_counter')

            assert resp.status_int == 200
            assert 'x_session' in self.app.cookies

            for x in range(1, 10):
                resp = resp.goto('/inc_count')
                assert resp.status_int == 200
                assert resp.text == str(x)


if __name__ == '__main__':
    unittest.main()
