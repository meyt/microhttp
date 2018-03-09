import unittest
from nanohttp import Controller, html
from microhttp import Application as BaseApplication
from microhttp.ext import log
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self):
                log.exception('there is an exception')
                log.error('there is an error')
                log.info('there is an info message')
                log.critical('there is a critical message')
                log.debug('there is a debug message')
                log.warning('there is a warning message')
                log.get_logger().warning('another warning message')
                return ''

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)

    def test_log(self):
        self.app.get('/', status=200)

    @classmethod
    def tearDownClass(cls):
        log.close()


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
