import unittest
import webtest
from os.path import dirname, join
from nanohttp import Controller
from microhttp import Application as BaseApplication


class WebTestCase(unittest.TestCase):
    stuff_dir = join(dirname(dirname(__file__)), 'stuff')
    _app_instance = None

    class Application(BaseApplication):
        class Root(Controller):
            pass

        def __init__(self):
            super().__init__(
                root=self.Root(),
            )

    @classmethod
    def create_test_app(cls):
        cls.app = webtest.TestApp(cls._app_instance)

    @classmethod
    def setUpClass(cls):
        cls._app_instance = cls.Application()
        cls._app_instance.configure(force=True)
        cls.create_test_app()
