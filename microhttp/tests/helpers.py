import unittest
import webtest
from nanohttp import Controller
from microhttp import Application as BaseApplication


class WebTestCase(unittest.TestCase):

    class Application(BaseApplication):
        class Root(Controller):
            pass

        def __init__(self):
            super().__init__(
                root=self.Root(),
            )

    def create_test_app(self):
        self.app = webtest.TestApp(self._app_instance)

    def setUp(self):
        self._app_instance = self.Application()
        self._app_instance.configure(force=True)
        self.create_test_app()
