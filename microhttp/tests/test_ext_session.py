import unittest
from nanohttp import Controller, text, settings, HttpBadRequest
from microhttp import Application as BaseApplication
from microhttp.ext import session
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):

            @text
            def init_counter(self):
                with session.get_session() as s:
                    s['counts'] = 0
                    s['temp'] = 0
                    del s['temp']
                    return s.get('counts')

            @text
            def inc_count(self):
                with session.get_session() as s:
                    if 'counts' in s:
                        s['counts'] += 1
                        return str(s['counts'])
                    else:
                        raise HttpBadRequest('counter not initialized')

            @text
            def has_counter(self):
                with session.get_session() as s:
                    if 'counts' in s:
                        return 'True'
                    else:
                        return 'False'

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)
            settings.merge("""
                session:
                  dogpile:  
                    backend: dogpile.cache.dbm
                    expiration_time: 3600
                    arguments:
                      filename:  %(microhttp_dir)s/tests/stuff/sessions.dbm
                  cookie_name: x_session
            """)
            session.configure()

    def test_simple(self):
        resp = self.app.get('/init_counter')
        self.assertEqual(resp.status_int, 200)
        self.assertIn('x_session', self.app.cookies)
        for x in range(1, 10):
            resp = resp.goto('/inc_count')
            self.assertEqual(resp.status_int, 200)
            self.assertEqual(resp.text, str(x))

    def test_advanced(self):
        for _ in range(20):
            self.create_test_app()
            resp = self.app.get('/has_counter')
            self.assertEqual(resp.status_int, 200)
            self.assertEqual(resp.text, 'False')

            self.app.get('/inc_count', status=400)

            resp = self.app.get('/init_counter')
            self.assertEqual(resp.status_int, 200)
            self.assertIn('x_session', self.app.cookies)

            resp = resp.goto('/has_counter')
            self.assertEqual(resp.status_int, 200)
            self.assertEqual(resp.text, 'True')

            for x in range(1, 10):
                resp = resp.goto('/inc_count')
                self.assertEqual(resp.status_int, 200)
                self.assertEqual(resp.text, str(x))


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
