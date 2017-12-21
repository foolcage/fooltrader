import datetime
import logging
import os

import pandas as pd

from fooltrader import settings
from fooltrader.contract.data_contract import TICK_COLUNM
from fooltrader.contract.files_contract import get_tick_path
from fooltrader.settings import TIME_FORMAT_DAY

logger = logging.getLogger(__name__)


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
    encoding = settings.DOWNLOAD_TXT_ENCODING if settings.DOWNLOAD_TXT_ENCODING else detect_encoding(
        url='file://' + os.path.abspath(path)).get('encoding')
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


def detect_encoding(url):
    import urllib.request
    from chardet.universaldetector import UniversalDetector

    usock = urllib.request.urlopen(url)
    detector = UniversalDetector()
    for line in usock.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    usock.close()
    return detector.result.get('encoding')


def is_available_tick(path):
    encoding = settings.DOWNLOAD_TXT_ENCODING if settings.DOWNLOAD_TXT_ENCODING else detect_encoding(
        url='file://' + os.path.abspath(path)).get('encoding')
    try:
        with open(path, encoding=encoding) as fr:
            line = fr.readline()
            return u'成交时间', u'成交价', u'价格变动', u'成交量(手)', u'成交额(元)', u'性质' == line.split()
    except Exception:
        return False


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


def to_float(str):
    try:
        return float(str)
    except Exception as e:
        return None


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
    df.columns = TICK_COLUNM
    df['direction'] = df['direction'].apply(lambda x: direction_to_int(x))
    df.to_csv(csv_path, index=False)


def get_file_name(the_path):
    return os.path.basename(the_path).split(".")[0]


def index_df_with_time(df, index='timestamp'):
    df = df.set_index(df[index])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def is_same_date(one, two):
    return pd.Timestamp(one).date() == pd.Timestamp(two).date()


def get_current_report_date():
    today = datetime.datetime.today().date()
    if today.month > 10:
        return "{}{}".format(today.year, '0930')
    elif today.month > 7:
        return "{}{}".format(today.year, '0630')
    elif today.month > 4:
        return "{}{}".format(today.year, '0331')
    else:
        return "{}{}".format(today.year - 1, '1231')
