import pandas

from fooltrader.contract import files_contract


def get_security_list(security_type='stock', exchanges=['sh', 'sz']):
    df = pandas.DataFrame()
    for exchange in exchanges:
        df1 = pandas.read_csv(files_contract.get_security_list_path(security_type, exchange), converters={'code': str})
        df1['exchange'] = exchange
        df1['type'] = security_type
        df = df.append(df1, ignore_index=True)
    df['id'] = df[['type', 'exchange', 'code']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
    return df


if __name__ == '__main__':
    print(get_security_list())
