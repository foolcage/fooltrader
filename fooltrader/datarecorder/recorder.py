# -*- coding: utf-8 -*-


class Recorder(object):
    security_type = None
    exchanges = None
    symbols = None

    def __init__(self, config={}) -> None:
        self.security_type = dict() if self.security_type is None else self.security_type

    def record_security(self):
        pass

    def record_tick(self):
        pass

    def record_kdata(self):
        pass
