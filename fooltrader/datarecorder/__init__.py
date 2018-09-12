import os

import pandas as pd

from fooltrader import get_exchange_dir
from fooltrader.contract.files_contract import get_security_list_path

df = pd.DataFrame()

# 去中心化交易所
df = df.append(
    {
        'code': 'RAM-EOS',
        'name': 'RAM/EOS',
        'listDate': '2018-06-09',
        'timestamp': '2018-06-09',
        'exchange': 'contract',
        'type': 'coin',
        'id': "cryptocurrency_contract_RAM-EOS"
    }, ignore_index=True)

if not df.empty:
    the_dir = get_exchange_dir(security_type='coin', exchange='contract')
    if not os.path.exists(the_dir):
        os.makedirs(the_dir)
    df.to_csv(get_security_list_path(security_type='coin', exchange='contract'),
              index=False)
