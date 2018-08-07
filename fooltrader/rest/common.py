# -*- coding: utf-8 -*-
from flask import jsonify


def error(err, *msg_args):
    if msg_args:
        return jsonify({"code": err['code'], "msg": err['msg'].format(*msg_args)})
    else:
        return jsonify({"code": err['code'], "msg": err['msg']})


def success(payload):
    return jsonify({"code": 0,
                    "msg": "success",
                    "payload": payload
                    })
