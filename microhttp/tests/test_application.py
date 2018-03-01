import unittest

from nanohttp import Controller, html

from microhttp import Application as BaseApplication
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self):
                return ''

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            kwargs.update({
                'context': {
                    'debug': True
                }
            })
            super().configure(*args, **kwargs)

    def test_simple(self):
        self.app.get('/', status=200)


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
