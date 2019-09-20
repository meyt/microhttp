from os.path import join

from pytest import fixture

from mock import patch

from nanohttp import Controller, settings, html, context, HTTPBadRequest

from microhttp import Application
from microhttp.ext import template, email
from microhttp.tests.helpers import SMTP


class DemoApplication(Application):
    class Root(Controller):
        @html
        def simple_email(self):
            with email.Email("main") as e:
                e.send(
                    to="recipient@example.com",
                    from_="sender@example.com",
                    subject="Welcome",
                    message="Welcome to this site",
                )
                yield "success"

        @html
        def email_with_template(self):
            with email.EmailTemplate("main") as e:
                e.send(
                    to="recipient@example.com",
                    cc=["recipient2@example.com"],
                    from_="sender@example.com",
                    subject="Welcome",
                    message="Welcome to this site",
                    filename="welcome.mako",
                    data={"username": "Steve"},
                )
                yield "success"

        @html
        def dynamic_params(self):
            # noinspection PyBroadException
            try:
                with email.Email(email.get_providers()["main"]) as e:
                    e.send(**dict(context.form))
                    yield "success"
            except Exception:
                raise HTTPBadRequest

    def __init__(self):
        super().__init__(self.Root())

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        settings.merge(
            """
            template:
                email:
                    directories:
                        - %(microhttp_dir)s/tests/stuff/email_template

            email:
                main:
                    host: example.com
                    port: 587
                    username: test@example.com
                    password: 123456
        """
        )
        template.configure()
        email.configure()


@fixture(scope="module")
def app(webtest):
    webtest.setup_application(DemoApplication)
    yield webtest.app


@patch("microhttp.ext.email.smtplib.SMTP", SMTP)
def test_simple(app):
    app.post("/simple_email", status=200)


@patch("microhttp.ext.email.smtplib.SMTP", SMTP)
def test_with_template(app):
    app.post("/email_with_template", status=200)
    assert "Steve welcome to example.com" in SMTP().inbox[-1].fullmessage


@patch("microhttp.ext.email.smtplib.SMTP", SMTP)
def test_dynamic_params(app, webtest):
    # Success email
    app.post(
        "/dynamic_params",
        status=200,
        params={
            "to": "recipient@example.com",
            "from_": "sender@example.com",
            "subject": "Welcome",
            "message": "welcome to example.com",
        },
    )

    # Missing message
    app.post(
        "/dynamic_params",
        status=400,
        params={
            "to": "recipient@example.com",
            "from_": "sender@example.com",
            "subject": "Welcome",
        },
    )

    # Attach files
    app.post_json(
        "/dynamic_params",
        status=200,
        params={
            "to": "recipient@example.com",
            "from_": "sender@example.com",
            "subject": "Welcome",
            "message": "welcome to example.com",
            "files": [join(webtest.stuff_dir, "img1.png")],
        },
    )
