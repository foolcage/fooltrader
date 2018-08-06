import pandas as pd

from fooltrader import get_security_list_path

df = pd.DataFrame()

# 去中心化交易所
df = df.append(
    {
        'code': 'RAM-EOS',
        'name': 'RAM/EOS',
        'listDate': '2018-06-09',
        'timestamp': '2018-06-09',
        'exchange': 'contract',
        'type': 'cryptocurrency',
        'id': "cryptocurrency_contract_RAM-EOS"
    }, ignore_index=True)

if not df.empty:
    df.to_csv(get_security_list_path(security_type='cryptocurrency', exchange='contract'),
              index=False)
