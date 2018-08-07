# -*- coding: utf-8 -*-

import datetime
import logging
import os
from logging.handlers import RotatingFileHandler

import pandas as pd

from fooltrader.contract.data_contract import TICK_COL
from fooltrader.contract.files_contract import get_tick_path
from fooltrader.settings import TIME_FORMAT_DAY, TIME_FORMAT_MICRO

logger = logging.getLogger(__name__)


def get_security_id(security_type, exchange, code):
    return "{}_{}_{}".format(security_type, exchange, code)


def init_process_log(file_name, log_dir=None):
    root_logger = logging.getLogger()

    # reset the handlers
    root_logger.handlers = []

    root_logger.setLevel(logging.INFO)

    if log_dir:
        file_name = os.path.join(log_dir, file_name)

    fh = RotatingFileHandler(file_name, maxBytes=524288000, backupCount=10)

    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(levelname)s  %(threadName)s  %(asctime)s  %(name)s:%(lineno)s  %(funcName)s  %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # filter
    # fh.addFilter(logging.Filter('fooltrader'))

    # add the handlers to the logger
    root_logger.addHandler(fh)
    root_logger.addHandler(ch)


def chrome_copy_header_to_dict(src):
    lines = src.split('\n')
    header = {}
    if lines:
        for line in lines:
            try:
                index = line.index(':')
                key = line[:index]
                value = line[index + 1:]
                if key and value:
                    header.setdefault(key.strip(), value.strip())
            except Exception:
                pass
    return header


def generate_csv_line(*items):
    if items:
        result = items[0]
        for item in items[1:]:
            result = '{},{}'.format(result, item)
        return result
    return ''


def gen_security_id(type, exchange, code):
    return type + '_' + exchange + '_' + code


# 对于开盘涨停的，算作买盘tick
def kdata_to_tick(kdata_json):
    str = '''成交时间	成交价	价格变动	成交量(手)	成交额(元)	性质
{}	{}	--	{}	{}	{}'''.format('09:25:00', kdata_json['high'], int(kdata_json['volume']) / 100,
                                           kdata_json['turnover'], '买盘')
    return str


def get_tick_item(path, the_date, security_item):
    encoding = 'GB2312'
    with open(path, encoding=encoding) as fr:
        lines = fr.readlines()
        for line in reversed(lines[1:]):
            tmp_timestamp, price, tmp_change, volume, turnover, tmp_direction = line.split()
            # timestamp = datetime.datetime.strptime(the_date + tmp_timestamp, '%Y-%m-%d%H:%M:%S')
            timestamp = the_date + " " + tmp_timestamp
            change = 0
            if not tmp_change == '--':
                change = float(tmp_change)
            direction = 0
            if tmp_direction == '买盘':
                direction = 1
            elif tmp_direction == '卖盘':
                direction = -1

            # yield SecurityItem(code_id='sh' + code, code=code, name=name, list_date=list_date, exchange='sh',
            #                    type='stock')
            # yield generate_csv_line(code, name, list_date, 'sh', 'stock')
            yield {"securityId": security_item['id'],
                   "code": security_item['code'],
                   "timestamp": timestamp,
                   "price": price,
                   "change": change,
                   "direction": direction,
                   "volume": volume,
                   "turnover": turnover}


def get_datetime(str):
    return datetime.datetime.strptime(str, TIME_FORMAT_DAY)


def get_year_quarter(time):
    if type(time) == str:
        time = get_datetime(time)
    return time.year, ((time.month - 1) // 3) + 1


def get_quarters(start, end=datetime.date.today()):
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


def fill_doc_type(doc_type, json_object):
    for key in json_object:
        doc_type[key] = json_object[key]


def to_float(str, default=None):
    try:
        return float(str.replace(',', ''))
    except Exception as e:
        return default


def get_exchange(code):
    if code >= '333333':
        return 'sh'
    else:
        return 'sz'


def direction_to_int(direction):
    if direction == '买盘':
        return 1
    elif direction == '卖盘':
        return -1
    else:
        return 0


def read_csv(f, encoding, sep=None, na_values=None):
    try:
        if sep:
            return pd.read_csv(f, sep=sep, encoding=encoding, na_values=na_values)
        else:
            return pd.read_csv(f, encoding=encoding, na_values=na_values)
    except UnicodeDecodeError as e:
        if encoding == "GB2312":
            return read_csv(f, "GBK")
        elif encoding == "GBK":
            return read_csv(f, "GB18030")
        elif encoding == "GB18030":
            return read_csv(f, "UTF-8")
        else:
            raise e


def sina_tick_to_csv(security_item, the_content, the_date):
    csv_path = get_tick_path(security_item, the_date)
    df = read_csv(the_content, "GB2312", sep='\s+')
    df = df.loc[:, ['成交时间', '成交价', '成交量(手)', '成交额(元)', '性质']]
    df.columns = TICK_COL
    df['direction'] = df['direction'].apply(lambda x: direction_to_int(x))
    df.to_csv(csv_path, index=False)


def get_file_name(the_path):
    return os.path.basename(the_path).split(".")[0]


def index_df_with_time(df, index='timestamp'):
    df = df.set_index(df[index], drop=False)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def is_same_date(one, two):
    return to_timestamp(one).date() == to_timestamp(two).date()


def is_same_time(one, two):
    return to_timestamp(one) == to_timestamp(two)


def get_report_period(the_date=datetime.datetime.today().date()):
    if the_date.month >= 10:
        return "{}{}".format(the_date.year, '-09-30')
    elif the_date.month >= 7:
        return "{}{}".format(the_date.year, '-06-30')
    elif the_date.month >= 4:
        return "{}{}".format(the_date.year, '-03-31')
    else:
        return "{}{}".format(the_date.year - 1, '-12-31')


# ms(int) or second(float) or str
def to_timestamp(the_time):
    if type(the_time) == int:
        the_time = the_time / 1000.0

    if type(the_time) == float:
        return pd.Timestamp.fromtimestamp(the_time)

    return pd.Timestamp(the_time)


def to_time_str(the_time, time_fmt=TIME_FORMAT_DAY):
    try:
        if time_fmt == TIME_FORMAT_MICRO:
            return to_timestamp(the_time).strftime(time_fmt)[0:-3]
        else:
            return to_timestamp(the_time).strftime(time_fmt)
    except Exception as e:
        return the_time


def to_epoch_millis(the_time):
    return int(to_timestamp(the_time).timestamp() * 1000)


def next_date(the_time):
    return to_timestamp(the_time) + datetime.timedelta(days=1)


def drop_duplicate(the_list):
    return list(set(the_list))


if __name__ == '__main__':
    aa = chrome_copy_header_to_dict(
        '''
        Host: www.nasdaq.com
        Connection: keep-alive
        Content-Length: 13
        Accept: */*
        Origin: http://www.nasdaq.com
        X-Requested-With: XMLHttpRequest
        User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
        Content-Type: application/json
        Referer: http://www.nasdaq.com/symbol/baba/historical
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.8,en;q=0.6
        ''')
    print(aa)
