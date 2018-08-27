# -*- coding: utf-8 -*-
import datetime

import arrow
import pandas as pd

CHINA_TZ = 'Asia/Shanghai'

TIME_FORMAT_ISO8601 = "YYYY-MM-DDTHH:mm:ss.SSSZ"

TIME_FORMAT_SEC = 'YYYY-MM-DD HH:mm:ss'

TIME_FORMAT_DAY = 'YYYY-MM-DD'


# ms(int) or second(float) or str
def to_timestamp(the_time, tz=CHINA_TZ):
    if type(the_time) == int:
        return pd.Timestamp(the_time, unit='ms', tz=tz)

    if type(the_time) == float:
        return pd.Timestamp(the_time, unit='s', tz=tz)

    return pd.Timestamp(the_time, tz=tz)


def to_time_str(the_time, time_fmt=TIME_FORMAT_ISO8601):
    try:
        return arrow.get(to_timestamp(the_time)).format(time_fmt)
    except Exception as e:
        return the_time


def current_timestamp(tz=CHINA_TZ):
    return pd.Timestamp.now(tz=tz)


def next_date(the_time):
    return to_timestamp(the_time) + datetime.timedelta(days=1)


def is_same_date(one, two):
    return to_timestamp(one).date() == to_timestamp(two).date()


def compare_timestamp(one, two):
    if to_timestamp(one) > to_timestamp(two):
        return 1
    if to_timestamp(one) == to_timestamp(two):
        return 0
    if to_timestamp(one) < to_timestamp(two):
        return -1


def get_year_quarter(time):
    time = to_timestamp(time)
    return time.year, ((time.month - 1) // 3) + 1


def get_quarters(start, end=current_timestamp()):
    start_year_quarter = get_year_quarter(start)
    current_year_quarter = get_year_quarter(end)
    if current_year_quarter[0] == start_year_quarter[0]:
        return [(current_year_quarter[0], x) for x in range(start_year_quarter[1], current_year_quarter[1] + 1)]
    elif current_year_quarter[0] - start_year_quarter[0] == 1:
        return [(start_year_quarter[0], x) for x in range(start_year_quarter[1], 5)] + \
               [(current_year_quarter[0], x) for x in range(1, current_year_quarter[1] + 1)]
    elif current_year_quarter[0] - start_year_quarter[0] > 1:
        return [(start_year_quarter[0], x) for x in range(start_year_quarter[1], 5)] + \
               [(x, y) for x in range(start_year_quarter[0] + 1, current_year_quarter[0]) for y in range(1, 5)] + \
               [(current_year_quarter[0], x) for x in range(1, current_year_quarter[1] + 1)]
    else:
        raise Exception("wrong start time:{}".format(start))
