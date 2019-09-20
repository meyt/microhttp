from os.path import join

from pytest import fixture

from nanohttp import Controller, html

from microhttp import Application


class DemoApplication(Application):
    class Root(Controller):
        @html
        def index(self):
            return ""

    def __init__(self):
        super().__init__(self.Root())

    def configure(self, *args, **kwargs):
        kwargs.update({"context": {"debug": True}})
        super().configure(*args, **kwargs)


@fixture(scope="module")
def app(webtest):
    webtest.setup_application(DemoApplication)
    yield webtest.app


def test_simple(app):
    app.get("/", status=200)


def test_configuration_files(webtest):
    app = DemoApplication()
    app.configure(
        files=[join(webtest.stuff_dir, "sample-config.yaml")], force=True
    )
