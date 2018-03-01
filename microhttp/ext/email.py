"""
    SMTP Email Extension
    Usage:
    
    Config:YAML
        email:
            my_provider:
                 host: example.com
                 port: 587
                 username: xyz
                 password: blah
                 
    Email with plain text message:
    >>>    with Email(get_providers()['my_provider']) as e:
    >>>        e.send(to='x@x.com', message='Hello plain')
    
    
    Email with HTML rendered content by Mako (Colony default template extension):
    >>>    with EmailTemplate('my_provider') as e:
    >>>        e.send(to='x@x.com', message='Hello plain',
    >>>               filename='test.mako', data={'junk':'yes'})
"""

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union
from os.path import basename
from nanohttp import settings
from microhttp import bus
from microhttp.ext.template import Template
import smtplib


class EmailProvider:
    host = ''
    port = 587
    username = ''
    password = ''
    mail = None

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def connect(self):
        self.mail = smtplib.SMTP(self.host, self.port)
        self.mail.ehlo()
        self.mail.starttls()
        self.mail.login(self.username, self.password)

    def disconnect(self):
        self.mail.quit()

    def send(self, to: str, message_plain: str, from_: str= '',
             cc: list=None, message_html: str=None,
             subject: str='', files: list=None):
        msg = MIMEMultipart('alternative')
        msg['From'] = from_
        msg['To'] = to

        if isinstance(cc, list):
            to = [to].extend(cc)
            msg['CC'] = ",".join(cc)

        msg['Subject'] = subject
        msg.attach(MIMEText(message_plain, 'plain'))

        if message_html is not None:
            msg.attach(MIMEText(message_html, 'html'))

        if isinstance(files, list):
            for file_path in files:
                file_name = basename(file_path)
                with open(file_path, 'rb') as fil:
                    part = MIMEApplication(
                        fil.read(),
                        Name=file_name
                    )
                    part['Content-Disposition'] = 'attachment; filename="%s"' % file_name
                    msg.attach(part)

        self.mail.sendmail(from_, to, msg.as_string())


class Email:

    def __init__(self, provider: Union[EmailProvider, str]):
        self.provider = bus.ext.email.providers[provider] if isinstance(provider, str) else provider

    def send(self, to: str, message: str,
             message_html: str=None, from_: str = '',
             cc: list=None, subject: str='', files: list=None):

        self.provider.send(to=to, from_=from_, cc=cc,
                           message_plain=message, message_html=message_html,
                           subject=subject, files=files)

    def __enter__(self):
        self.provider.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.provider.disconnect()


class EmailTemplate:

    def __init__(self, provider: Union[EmailProvider, str]):
        self.provider = bus.ext.email.providers[provider] if isinstance(provider, str) else provider
        self.template = Template()

    def send(self, to: str, message: str, filename: str, data: dict,
             from_: str = '', cc: list = None,
             subject: str = '', files: list = None):
        message_html = self.template.render(filename=filename, data=data)
        self.provider.send(to=to, from_=from_, cc=cc,
                           message_plain=message, message_html=message_html,
                           subject=subject, files=files)

    def __enter__(self):
        self._variables = {}
        self.provider.connect()
        self.template.set_template('email')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.provider.disconnect()


def configure():
    bus.ext.email.providers = {}
    for provider_name, provider_spec in settings.email.items():
        bus.ext.email.providers[provider_name] = EmailProvider(**provider_spec)


def get_providers() -> dict:
    return bus.ext.email.providers
