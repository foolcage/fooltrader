import datetime

import pandas

from fooltrader import settings
from fooltrader.contract import files_contract
from fooltrader.datasource import tdx
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils import utils


def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=STOCK_START_CODE, end=STOCK_END_CODE):
    df = pandas.DataFrame()
    for exchange in exchanges:
        df1 = pandas.read_csv(files_contract.get_security_list_path(security_type, exchange), converters={'code': str})
        df = df.append(df1, ignore_index=True)
    df = df[df["code"] <= end]
    df = df[df["code"] >= start]
    return df


def get_kdata(security_item, start, end):
    df = pandas.DataFrame()
    for year, quarter in utils.get_quarters(start, end):
        data_path = files_contract.get_kdata_path_csv(security_item, year, quarter)
        df1 = pandas.read_csv(data_path, converters={'code': str})
        df = df.append(df1, ignore_index=True)
    return df


if __name__ == '__main__':
    item = {"code": "000001", "type": "stock", "exchange": "sz"}
    df1 = get_kdata(item,
                    datetime.datetime.strptime('1991-04-01', settings.TIME_FORMAT_DAY),
                    datetime.datetime.strptime('1991-12-31', settings.TIME_FORMAT_DAY))
    df1 = df1.set_index(df1['timestamp'])
    df1 = df1.sort_index()
    print(df1)

    df2 = tdx.get_tdx_kdata(item, '1991-04-01', '1991-12-31')
    df2 = df2.set_index(df2['timestamp'])
    df2 = df2.sort_index()
    print(df2)

    for _, data in df1.iterrows():
        if data['timestamp'] in df2.index:
            data2 = df2.loc[data['timestamp']]
            assert data2["low"] == data["low"]
            assert data2["open"] == data["open"]
            assert data2["high"] == data["high"]
            assert data2["close"] == data["close"]
            assert data2["volume"] == data["volume"]
            try:
                assert data2["turnover"] == data["turnover"]
            except Exception as e:
                print(data2["turnover"])
                print(data["turnover"])
