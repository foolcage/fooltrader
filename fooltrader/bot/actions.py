# -*- coding: utf-8 -*-
import email
import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from fooltrader.settings import SMTP_HOST, SMTP_PORT, EMAIL_PASSWORD, EMAIL_USER_NAME


class Action(object):
    logger = logging.getLogger(__name__)

    def send_message(self, to_user, title, body, **kwargs):
        pass


class EmailAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.client = smtplib.SMTP()
        self.client.connect(SMTP_HOST, SMTP_PORT)
        self.client.login(EMAIL_USER_NAME, EMAIL_PASSWORD)

    def send_message(self, to_user, title, body, **kwargs):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(title).encode()
        msg['From'] = "{} <{}>".format(Header('fooltrader').encode(), EMAIL_USER_NAME)
        msg['To'] = to_user

        msg['Message-id'] = email.utils.make_msgid()
        msg['Date'] = email.utils.formatdate()

        plain_text = MIMEText(body, _subtype='plain', _charset='UTF-8')
        msg.attach(plain_text)

        try:
            self.client.sendmail(EMAIL_USER_NAME, to_user, msg.as_string())
        except Exception as e:
            self.logger.error('send email failed', e)


class WeixinAction(Action):
    WEIXIN_TOKEN = 'aaa'
    GET_TEMPLATE_URL = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token={}".format(
        WEIXIN_TOKEN)
    SEND_MSG_URL = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(WEIXIN_TOKEN)

    {
        "touser": "OPENID",
        "template_id": "ngqIpbwh8bUfcSsECmogfXcV14J0tQlEpBO27izEYtY",
        "url": "http://weixin.qq.com/download",
        "miniprogram": {
            "appid": "xiaochengxuappid12345",
            "pagepath": "index?foo=bar"
        },
        "data": {
            "first": {
                "value": "恭喜你购买成功！",
                "color": "#173177"
            },
            "keyword1": {
                "value": "巧克力",
                "color": "#173177"
            },
            "keyword2": {
                "value": "39.8元",
                "color": "#173177"
            },
            "keyword3": {
                "value": "2014年9月22日",
                "color": "#173177"
            },
            "remark": {
                "value": "欢迎再次购买！",
                "color": "#173177"
            }
        }
    }

    def send_message(self, to_user, title, body, **kwargs):
        template_id = 'aaa'
        the_json = {
            "touser": to_user,
            "template_id": template_id,
            "url": "http://www.foolcage.com",
            "data": {
                "first": {
                    "value": "恭喜你购买成功！",
                    "color": "#173177"
                },
                "keyword1": {
                    "value": "巧克力",
                    "color": "#173177"
                },
                "keyword2": {
                    "value": "39.8元",
                    "color": "#173177"
                },
                "keyword3": {
                    "value": "2014年9月22日",
                    "color": "#173177"
                },
                "remark": {
                    "value": "欢迎再次购买！",
                    "color": "#173177"
                }
            }
        }
        requests.post(self.SEND_MSG_URL, the_json)
