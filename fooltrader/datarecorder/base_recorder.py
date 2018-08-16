# -*- coding: utf-8 -*-

class BaseRecorder(object):
    def record_security(self):
        pass

    def record_tick(self):
        pass

    def record_kdata(self):
        pass

    @staticmethod
    def generate_security_item(security_type, exchange, code, name, list_date=None):
        return {
            'code': code,
            'name': name,
            'listDate': list_date,
            'timestamp': list_date,
            'exchange': exchange,
            'type': security_type,
            'id': "{}_{}_{}".format(security_type, exchange, code)
        }
