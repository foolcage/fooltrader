# -*- coding: utf-8 -*-
from datetime import timedelta

import pandas as pd

from fooltrader.bot.bot import NotifyEventBot
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_statistic_index
from fooltrader.domain.data.es_quote import CommonKData
from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.es_utils import es_get_latest_timestamp
from fooltrader.utils.utils import to_timestamp, to_time_str, fill_doc_type


class StatisticBot(NotifyEventBot):

    def on_init(self):
        super().on_init()
        self.security_id = 'cryptocurrency_contract_RAM-EOS'

        query = {
            "term": {"securityId": ""}
        }
        query["term"]["securityId"] = self.security_id

        # get latest kdata timestamp
        self.kdata_index_name = get_es_kdata_index(security_type='cryptocurrency', exchange='contract', level='1min')
        latest_kdata_timestamp = es_get_latest_timestamp(index=self.kdata_index_name, query=query)

        # get latest statistic timestamp
        self.statistic_index_name = get_es_statistic_index(security_type='cryptocurrency', exchange='contract')
        latest_statistic_timestamp = es_get_latest_timestamp(index=self.statistic_index_name, query=query)

        if latest_kdata_timestamp != latest_statistic_timestamp:
            self.logger.warning("latest_kdata_timestamp:{},latest_statistic_timestamp:{}".format(latest_kdata_timestamp,
                                                                                                 latest_statistic_timestamp))

        if latest_kdata_timestamp and latest_statistic_timestamp:
            self.start_timestamp = min(latest_kdata_timestamp, latest_statistic_timestamp)

        if not self.start_timestamp:
            self.start_timestamp = to_timestamp('2018-06-09 11:55:00')

    def after_init(self):
        super().after_init()
        self.last_timestamp = None
        self.df = pd.DataFrame()

    def on_event(self, event_item):
        if not self.last_timestamp:
            self.last_timestamp = to_timestamp(event_item['timestamp'])

        current_timestamp = to_timestamp(event_item['timestamp'])

        # calculating last minute
        if current_timestamp.minute != self.last_timestamp.minute:
            # generating kdata
            se_price = self.df['price']
            high = se_price.max()
            low = se_price.min()
            open = se_price[0]
            close = se_price[len(se_price) - 1]
            volume = self.df['volume'].sum()
            turnover = self.df['turnover'].sum()

            kdata_timestamp = self.last_timestamp + timedelta(minutes=1, seconds=-self.last_timestamp.second,
                                                              microseconds=-self.last_timestamp.microsecond)
            time_str = to_time_str(kdata_timestamp, time_fmt=TIME_FORMAT_MICRO)
            doc_id = "{}_{}".format(self.security_id, time_str)
            kdata_json = {
                'id': doc_id,
                'timestamp': time_str,
                'securityId': self.security_item['id'],
                'code': self.security_item['code'],
                'name': self.security_item['name'],
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume,
                'turnover': turnover
            }

            kdata_doc = CommonKData(meta={'id': doc_id, 'index': self.kdata_index_name})

            fill_doc_type(kdata_doc, kdata_json)

            kdata_doc.save(force=True)

            self.last_timestamp = current_timestamp
            self.df = pd.DataFrame()

        self.df = self.df.append(event_item, ignore_index=True)


if __name__ == '__main__':
    StatisticBot().run()
