from pytest import fixture

from nanohttp import Controller, html

from microhttp import Application
from microhttp.ext import log


class DemoApplication(Application):
    class Root(Controller):
        @html
        def index(self):
            log.exception("there is an exception")
            log.error("there is an error")
            log.info("there is an info message")
            log.critical("there is a critical message")
            log.debug("there is a debug message")
            log.warning("there is a warning message")
            log.get_logger().warning("another warning message")
            return ""

    def __init__(self):
        super().__init__(self.Root())

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)


@fixture(scope="module")
def app(webtest):
    webtest.setup_application(DemoApplication)
    yield webtest.app
    log.close()


def test_log(app):
    app.get("/", status=200)
