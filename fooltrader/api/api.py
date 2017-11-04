import pandas

from fooltrader.contract import files_contract


def get_security_list(security_type='stock', exchanges=['sh', 'sz']):
    df = pandas.DataFrame()
    for exchange in exchanges:
        df = df.append(
            pandas.read_csv(files_contract.get_security_list_path(security_type, exchange), converters={'code': str}),
            ignore_index=True)
    return df


if __name__ == '__main__':
    print(get_security_list())
