from microhttp import bus
from nanohttp import settings, context
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


class ReCaptchaException(Exception):
    pass


class SiteKeyError(ReCaptchaException):
    pass


class ReCaptcha:
    verify_server = 'https://www.google.com/recaptcha/api/siteverify'
    secret_key = ''
    site_key = '6Le7mxgUAAAAAPeIWi3VPq0vu46dhHmucIcemDfZ'
    remoteip = ''

    def __init__(self, secret_key, site_key, remoteip=''):
        self.secret_key = secret_key
        self.site_key = site_key
        self.remoteip = remoteip

    @staticmethod
    def get_html_head(async: bool=True, defer: bool=True, render: str='', hl: str='', onload: str=''):
        """
        Get HTML ReCaptcha Head
        :param async: bool
        :param defer: bool
        :param render: str Documented on https://developers.google.com/recaptcha/docs/display
        :param hl: str Documented on https://developers.google.com/recaptcha/docs/display
        :param onload: str Documented on https://developers.google.com/recaptcha/docs/display
        :return: str
        """
        async = ' async ' if async else ''
        defer = ' defer ' if defer else ''
        args = '?>'
        if render != '':
            args += '&render=%s' % render

        if hl != '':
            args += '&hl=%s' % hl

        if onload != '':
            args += '&onload=%s' % onload

        return '''<script src="https://www.google.com/recaptcha/api.js%s" %s %s></script>''' % (
            args,
            async,
            defer
        )

    def get_html_field(self, data_attributes: dict=None, enable_no_script: bool=False):
        """
        Get HTML Field of ReCaptcha
        :param data_attributes: dict Data attributes described in https://developers.google.com/recaptcha/docs/display
        :param enable_no_script: bool Show input for javascript-disabled browsers.
        https://developers.google.com/recaptcha/docs/faq#does-recaptcha-support-users-that-dont-have-javascript-enabled
        :return: str
        """
        if isinstance(data_attributes, dict):
            if 'data-sitekey' not in data_attributes:
                if self.site_key == '':
                    raise SiteKeyError('data-sitekey not entered')
                else:
                    data_attributes['data-sitekey'] = self.site_key
        else:
            if self.site_key == '':
                raise SiteKeyError('data-sitekey not entered')
            else:
                data_attributes = {
                    'data-sitekey': self.site_key
                }
        attributes = ''
        for attribute_name, attribute_value in data_attributes.items():
            attributes += '%s="%s" ' % (attribute_name, attribute_value)

        output = '<div class="g-recaptcha" %s ></div>' % attributes
        if enable_no_script:
            output += '''
            <noscript>
              <div>
                <div style="width: 302px; height: 422px; position: relative;">
                  <div style="width: 302px; height: 422px; position: absolute;">
                    <iframe src="https://www.google.com/recaptcha/api/fallback?k=%s"
                            frameborder="0" scrolling="no"
                            style="width: 302px; height:422px; border-style: none;">
                    </iframe>
                  </div>
                </div>
                <div style="width: 300px; height: 60px; border-style: none;
                               bottom: 12px; left: 25px; margin: 0px; padding: 0px; right: 25px;
                               background: #f9f9f9; border: 1px solid #c1c1c1; border-radius: 3px;">
                  <textarea id="g-recaptcha-response" name="g-recaptcha-response"
                               class="g-recaptcha-response"
                               style="width: 250px; height: 40px; border: 1px solid #c1c1c1;
                                      margin: 10px 25px; padding: 0px; resize: none;" >
                  </textarea>
                </div>
              </div>
            </noscript>
        ''' % data_attributes['data-sitekey']
        return output

    def verify(self) -> bool:
        """
        Verify Response
        :return: bool
        """
        if settings.debug:
            return True
        response_value = context.form.get('g-recaptcha-response', '')
        params = {
            'secret': self.secret_key,
            'response': response_value,
        }
        if self.remoteip != '':
            params['remoteip'] = self.remoteip

        http_response = urlopen(Request(
            url=self.verify_server,
            data=urlencode(params).encode('utf-8'),
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'ReCaptcha Python '
            }
        ))
        result = json.loads(http_response.read().decode())
        http_response.close()

        if result['success']:
            return True
        else:
            return False


def configure():
    from microhttp.ext import log
    log.warning('microhttp.ext.recaptcha deprecated')
    bus.ext.recaptcha = ReCaptcha(**settings.recaptcha)


def get_recaptcha() -> ReCaptcha:
    return bus.ext.recaptcha
