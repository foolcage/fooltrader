import pandas

from fooltrader.contract import files_contract
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE


def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=STOCK_START_CODE, end=STOCK_END_CODE):
    df = pandas.DataFrame()
    for exchange in exchanges:
        df1 = pandas.read_csv(files_contract.get_security_list_path(security_type, exchange), converters={'code': str})
        df = df.append(df1, ignore_index=True)
    df = df[df["code"] <= end]
    df = df[df["code"] >= start]
    return df


if __name__ == '__main__':
    print(get_security_list())
