# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

import elasticsearch.helpers
import pandas as pd

from fooltrader import es_client
from fooltrader.api.esapi.esapi import es_get_user_statistic, es_get_latest_daily_user_statistic
from fooltrader.bot.bot import NotifyEventBot
from fooltrader.contract.es_contract import get_cryptocurrency_user_statistic_index, \
    get_cryptocurrency_daily_user_statistic_index
from fooltrader.domain.data.es_quote import EosUserStatistic
from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.es_utils import es_get_latest_record, es_index_mapping
from fooltrader.utils.utils import to_timestamp, to_time_str, is_same_date

user_statistic_index_name = get_cryptocurrency_user_statistic_index()
daily_user_statistic_index_name = get_cryptocurrency_daily_user_statistic_index()

es_index_mapping(user_statistic_index_name, EosUserStatistic)
es_index_mapping(daily_user_statistic_index_name, EosUserStatistic)


class EosUserStatisticBot(NotifyEventBot):
    def on_init(self):
        super().on_init()
        self.security_id = 'cryptocurrency_contract_RAM-EOS'

        query = {
            "term": {"securityId": ""}
        }
        query["term"]["securityId"] = self.security_id

        # get latest user statistic timestamp
        latest_eos_user_statistic_record = es_get_latest_record(index=user_statistic_index_name,
                                                                query=query, time_field='updateTimestamp')

        if latest_eos_user_statistic_record:
            self.latest_eos_user_statistic_record = EosUserStatistic(
                meta={'id': latest_eos_user_statistic_record['id'], 'index': user_statistic_index_name},
                **latest_eos_user_statistic_record)

        else:
            self.latest_eos_user_statistic_record = None

        if self.latest_eos_user_statistic_record:
            self.start_timestamp = to_timestamp(self.latest_eos_user_statistic_record['updateTimestamp'])

        self.user_map_latest_user_statistic = {}
        self.user_map_latest_user_daily_statistic = {}
        self.es_actions = []

    def after_init(self):
        super().after_init()
        if not self.start_timestamp:
            self.start_timestamp = to_timestamp(self.security_item['listDate'])
        # the last timestamp for the computing interval
        self.last_timestamp = None
        self.last_day_time_str = None
        self.last_mirco_time_str = None

        self.df = pd.DataFrame()
        self.item_list = []

        self.computing_start = None

    def init_new_computing_interval(self, event_timestamp):
        self.last_timestamp = to_timestamp(event_timestamp)
        self.kdata_timestamp = self.last_timestamp + timedelta(seconds=-self.last_timestamp.second,
                                                               microseconds=-self.last_timestamp.microsecond)

        self.last_day_time_str = to_time_str(self.kdata_timestamp)
        self.last_mirco_time_str = to_time_str(self.kdata_timestamp, time_fmt=TIME_FORMAT_MICRO)

    def on_event(self, event_item):
        if not self.computing_start:
            self.computing_start = datetime.now()
        if not self.last_timestamp:
            self.init_new_computing_interval(event_item['timestamp'])

        current_timestamp = to_timestamp(event_item['timestamp'])

        # calculating last minute
        if current_timestamp.minute != self.last_timestamp.minute:
            self.df = pd.DataFrame(self.item_list)

            self.generate_user_statistic()

            if self.es_actions:
                resp = elasticsearch.helpers.bulk(es_client, self.es_actions)
                self.logger.info("index success:{} failed:{}".format(resp[0], len(resp[1])))
                if resp[1]:
                    self.logger.error("error:{}".format(resp[1]))

            self.init_new_computing_interval(event_item['timestamp'])
            self.es_actions = []
            self.item_list = []

            self.logger.info("using computing time:{}".format(datetime.now() - self.computing_start))
            self.computing_start = datetime.now()

        self.item_list.append(event_item)

    def update_statistic_doc(self, statistic_doc, append_record, updateTimestamp):
        for key in append_record.keys():
            if pd.isna(append_record[key]):
                the_value = 0
            else:
                the_value = append_record[key]

            if key in statistic_doc:
                statistic_doc[key] += float(the_value)
            else:
                statistic_doc[key] = float(the_value)
        statistic_doc['updateTimestamp'] = updateTimestamp
        # statistic_doc.save(force=True)
        self.es_actions.append(statistic_doc.to_dict(include_meta=True))

    def update_daily_user_statistic(self, user_id, record, update_timestamp):
        latest_user_daily_statistic = self.user_map_latest_user_daily_statistic.get(user_id)

        if not latest_user_daily_statistic:
            the_record = es_get_latest_daily_user_statistic(user_id=user_id)
            if the_record:
                latest_user_daily_statistic = EosUserStatistic(
                    meta={'id': the_record['id'], 'index': daily_user_statistic_index_name},
                    **the_record)
                self.user_map_latest_user_daily_statistic[user_id] = latest_user_daily_statistic

        # ignore the user statistic has computed before
        if latest_user_daily_statistic and self.kdata_timestamp <= to_timestamp(
                latest_user_daily_statistic['updateTimestamp']):
            return

        if not latest_user_daily_statistic or not is_same_date(latest_user_daily_statistic['timestamp'],
                                                               self.df['timestamp'][0]):
            doc_id = '{}_{}_{}'.format(user_id, self.security_id, self.last_day_time_str)
            latest_user_daily_statistic = EosUserStatistic(
                meta={'id': doc_id, 'index': daily_user_statistic_index_name},
                id=doc_id,
                userId=user_id,
                timestamp=self.last_day_time_str,
                securityId=self.security_id,
                code=self.security_item['code'],
                name=self.security_item['name'])
            self.user_map_latest_user_daily_statistic[user_id] = latest_user_daily_statistic

        # update user daily statistic
        self.update_statistic_doc(latest_user_daily_statistic, record, update_timestamp)

    def update_user_statistic(self, user_id, record, update_timestamp):
        latest_user_statistic = self.user_map_latest_user_statistic.get(user_id)
        if not latest_user_statistic:
            doc_id = '{}_{}'.format(user_id, self.security_id)

            the_record = es_get_user_statistic(user_id=user_id)
            if the_record:
                latest_user_statistic = EosUserStatistic(meta={'id': doc_id, 'index': user_statistic_index_name},
                                                         **the_record)
                self.user_map_latest_user_statistic[user_id] = latest_user_statistic
        # ignore the user statistic has computed before
        if latest_user_statistic and self.kdata_timestamp <= to_timestamp(
                latest_user_statistic['updateTimestamp']):
            return

        if not latest_user_statistic:
            latest_user_statistic = EosUserStatistic(meta={'id': doc_id, 'index': user_statistic_index_name},
                                                     id=doc_id,
                                                     userId=user_id,
                                                     timestamp=self.last_day_time_str,
                                                     securityId=self.security_id,
                                                     code=self.security_item['code'],
                                                     name=self.security_item['name'])
            self.user_map_latest_user_statistic[user_id] = latest_user_statistic

        # update user  statistic
        self.update_statistic_doc(latest_user_statistic, record, update_timestamp)

    def generate_user_statistic(self):
        self.df['volumeFlow'] = self.df['volume'] * self.df['direction']
        self.df['turnoverFlow'] = self.df['turnover'] * self.df['direction']

        df_sum = self.df.groupby('receiver').sum()
        df_sum_in = self.df[self.df['direction'] == 1].groupby('receiver').sum()
        df_sum_out = self.df[self.df['direction'] == -1].groupby('receiver').sum()

        for user in df_sum.index:
            record = {
                "volume": df_sum.loc[user, 'volumeFlow'],
                "turnover": df_sum.loc[user, 'turnoverFlow']
            }

            if not df_sum_in.empty and user in df_sum_in.index:
                record['volumeIn'] = df_sum_in.loc[user, 'volumeFlow']
                record['turnoverIn'] = df_sum_in.loc[user, 'turnoverFlow']
            else:
                record['volumeIn'] = 0
                record['turnoverIn'] = 0

            if not df_sum_out.empty and user in df_sum_out.index:
                record['volumeOut'] = df_sum_out.loc[user, 'volumeFlow']
                record['turnoverOut'] = df_sum_out.loc[user, 'turnoverFlow']
            else:
                record['volumeOut'] = 0
                record['turnoverOut'] = 0

            self.update_daily_user_statistic(user_id=user, record=record, update_timestamp=self.last_mirco_time_str)
            self.update_user_statistic(user_id=user, record=record, update_timestamp=self.last_mirco_time_str)


if __name__ == '__main__':
    EosUserStatisticBot().run()
