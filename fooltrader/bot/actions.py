# -*- coding: utf-8 -*-
import email
import json
import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from fooltrader.settings import SMTP_HOST, SMTP_PORT, EMAIL_PASSWORD, EMAIL_USER_NAME, WEIXIN_APP_ID, WEIXIN_APP_SECRECT


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
    GET_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
        WEIXIN_APP_ID, WEIXIN_APP_SECRECT)

    GET_TEMPLATE_URL = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token={}"
    SEND_MSG_URL = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}"

    token = None

    def __init__(self) -> None:
        self.refresh_token()

    def refresh_token(self):
        resp = requests.get(self.GET_TOKEN_URL)
        self.logger.info("refresh_token resp.status_code:{}, resp.text:{}".format(resp.status_code, resp.text))

        if resp.status_code == 200 and resp.json() and 'access_token' in resp.json():
            self.token = resp.json()['access_token']
        else:
            self.logger.error("could not refresh_token")

    def send_message(self, to_user, title, body, **kv):
        # 先固定一个template

        # {
        #     "template_id": "mkqi-L1h56mH637vLXiuS_ulLTs1byDYYgLBbSXQ65U",
        #     "title": "涨跌幅提醒",
        #     "primary_industry": "金融业",
        #     "deputy_industry": "证券|基金|理财|信托",
        #     "content": "{{first.DATA}}\n股票名：{{keyword1.DATA}}\n最新价：{{keyword2.DATA}}\n涨跌幅：{{keyword3.DATA}}\n{{remark.DATA}}",
        #     "example": "您好，腾新控股最新价130.50元，上涨达到设置的3.2%\r\n股票名：腾讯控股（00700）\r\n最新价：130.50元\r\n涨跌幅：+3.2%\r\n点击查看最新实时行情。"
        # }

        template_id = 'mkqi-L1h56mH637vLXiuS_ulLTs1byDYYgLBbSXQ65U'
        the_json = {
            "touser": to_user,
            "template_id": template_id,
            "url": "http://www.foolcage.com",
            "data": {
                "first": {
                    "value": title,
                    "color": "#173177"
                },
                "keyword1": {
                    "value": str(kv['name']),
                    "color": "#173177"
                },
                "keyword2": {
                    "value": str(kv['price']),
                    "color": "#173177"
                },
                "keyword3": {
                    "value": str(kv['change_pct']),
                    "color": "#173177"
                },
                "remark": {
                    "value": "你设置的提醒已触发",
                    "color": "#173177"
                }
            }
        }

        the_data = json.dumps(the_json, ensure_ascii=False).encode('utf-8')

        resp = requests.post(self.SEND_MSG_URL.format(self.token), the_data)

        self.logger.info("send weixin resp:{}".format(resp.text))

        if resp.json() and resp.json()["errcode"] == 0:
            self.logger.info("send weixin to user:{} data:{} success".format(to_user, the_json))
