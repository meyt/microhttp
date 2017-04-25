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

    def setUp(self):
        app = self.Application()
        app.configure(force=True)
        app.prepare()
        self.app = webtest.TestApp(app.wsgi())
