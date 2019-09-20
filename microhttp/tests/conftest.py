from os.path import dirname, join

from pytest import fixture

from webtest import TestApp

from microhttp import Application


class WebTestCase:
    stuff_dir = join(dirname(__file__), "stuff")

    def setup_application(self, application: Application):
        app = application()
        app.configure(force=True)
        self.app = TestApp(app, lint=False)


@fixture(scope="module")
def webtest():
    test_case = WebTestCase()
    yield test_case
