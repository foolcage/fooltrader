# -*- coding: utf-8 -*-
class Backend(object):
    def get_security_item(security_type='stock', exchange=None, code=None, start_date=None):
        pass

    def get_ticks(security_item, the_date=None, start_date=None, end_date=None):
        pass

    def get_kdata(security_item, the_date=None, start_date=None, end_date=None, level='day'):
        pass

    def get_latest_kdata_timestamp(self, security_item):
        pass

    def get_latest_tick_timestamp_order(self, security_item):
        pass
