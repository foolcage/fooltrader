import datetime
import os

import pandas as pd

from fooltrader import settings
from fooltrader.contract import files_contract
from fooltrader.datasource import tdx
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE


# meta
def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=STOCK_START_CODE, end=STOCK_END_CODE):
    df = pd.DataFrame()
    for exchange in exchanges:
        df1 = pd.read_csv(files_contract.get_security_list_path(security_type, exchange), converters={'code': str})
        df = df.append(df1, ignore_index=True)
    df = df[df["code"] <= end]
    df = df[df["code"] >= start]
    return df


# kdata
def get_kdata(security_item, start=None, end=None, fuquan=None, dtype=None):
    the_path = files_contract.get_kdata_path_csv(security_item, fuquan=fuquan)
    if os.path.isfile(the_path):
        if not dtype:
            dtype = {"code": str}
        df = pd.read_csv(the_path, dtype=dtype)
        df = df.set_index(df['timestamp'])
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.loc[start:end]
        return df
    return pd.DataFrame()


def kdata_exist(security_item, year, quarter, fuquan=None):
    df = get_kdata(security_item, fuquan=fuquan)
    if "{}Q{}".format(year, quarter) in df.index:
        return True
    return False


# TODO:use join
def merge_to_current_kdata(security_item, df, fuquan='bfq'):
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df1 = get_kdata(security_item, fuquan=fuquan, dtype=str)
    df1 = df1.append(df)

    df1 = df1.drop_duplicates()
    df1.sort_index()

    the_path = files_contract.get_kdata_path_csv(security_item, fuquan=fuquan)
    df1.to_csv(the_path, index=False)


# tick
if __name__ == '__main__':
    item = {"code": "000001", "type": "stock", "exchange": "sz"}
    assert kdata_exist(item, 1991, 2) == True
    assert kdata_exist(item, 1991, 3) == True
    assert kdata_exist(item, 1991, 4) == True
    assert kdata_exist(item, 1991, 2) == True
    assert kdata_exist(item, 1990, 1) == False
    assert kdata_exist(item, 2017, 1) == False

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
