from datetime import date

from pytest import fixture

from nanohttp import Controller, settings

from microhttp import Application
from microhttp.ext import template


class DemoApplication(Application):
    class Root(Controller):
        @template.render("simple.mako")
        def simple(self):
            template.set_template("test_dir1")
            return dict()

        @template.render("unicode.mako")
        def unicode(self):
            template.set_template("test_dir2")
            return dict()

        @template.render("advanced.mako")
        def advanced(self):
            template.set_template("test_dir2")
            return {"today": date.today()}

        @template.render("have_issues.mako")
        def have_issues(self):
            template.set_template("test_dir2")
            return {"today": date.today()}

        @template.render("have_issues2.mako")
        def missed_file(self):
            template.set_template("test_dir2")
            return {"today": date.today()}

        @template.render("advanced.mako")
        def invalid_data(self):
            template.set_template("test_dir2")
            return "success"

        @template.render("advanced.mako")
        def auto_to_dict(self):
            template.set_template("test_dir2")

            class Dummy:
                @staticmethod
                def to_dict():
                    return {}

            return Dummy

    def __init__(self):
        super().__init__(self.Root())

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        settings.merge(
            """
        template:
            test_dir1:
                directories:
                    - %(microhttp_dir)s/tests/stuff/template_dir1
            test_dir2:
                directories:
                    - %(microhttp_dir)s/tests/stuff/template_dir2
        """
        )
        template.configure()


@fixture(scope="module")
def app(webtest):
    webtest.setup_application(DemoApplication)
    return webtest.app


def test_simple(app):
    app.get("/simple", status=200)


def test_unicode(app):
    resp = app.get("/unicode")
    expected_output = (
        "Hallo wêreld, Здравей, свят, 世界您好, Ahoj světe, "
        "Γεια σου κόσμε, שלום לך עולם, हैलो वर्ल्डm ハローワールド,"
        "  , หวัดดีชาวโลก, Привіт, народ, سلام دنيا, Chào thế giới"
    )
    assert resp.text == expected_output


def test_advanced(app):
    resp = app.get("/advanced")
    assert resp.text == "<span>today: %s</span>" % date.today()


def test_auto_to_dict(app):
    app.get("/auto_to_dict")


def test_error_handling(app):
    settings.debug = True
    app.get("/have_issues")
    app.get("/missed_file")
    print(app.get("/invalid_data", status=500))

    settings.debug = False
    app.get("/have_issues", status=500)
    app.get("/missed_file", status=500)
    app.get("/invalid_data", status=500)
