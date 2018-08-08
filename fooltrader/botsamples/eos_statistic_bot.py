# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

import pandas as pd

from fooltrader.bot.bot import NotifyEventBot
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_statistic_index
from fooltrader.domain.data.es_quote import CommonKData, CommonStatistic
from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.es_utils import es_get_latest_timestamp, es_get_latest_record, es_index_mapping
from fooltrader.utils.utils import to_timestamp, to_time_str, fill_doc_type, is_same_date, is_same_time

statistic_index_name = get_es_statistic_index(security_type='cryptocurrency', exchange='contract')
kdata_index_name = get_es_kdata_index(security_type='cryptocurrency', exchange='contract', level='1min')

es_index_mapping(statistic_index_name, CommonStatistic)
es_index_mapping(kdata_index_name, CommonKData)


class EosStatisticBot(NotifyEventBot):
    BIG_ORDER = 2000 * 10000
    MIDDLE_ORDER = 500 * 10000

    def on_init(self):
        super().on_init()
        self.security_id = 'cryptocurrency_contract_RAM-EOS'

        query = {
            "term": {"securityId": ""}
        }
        query["term"]["securityId"] = self.security_id

        # get latest kdata timestamp
        latest_kdata_timestamp = es_get_latest_timestamp(index=kdata_index_name, query=query)

        # get latest eos statistic timestamp
        latest_statistic_record = es_get_latest_record(index=statistic_index_name,
                                                       query=query, time_field='updateTimestamp')
        if latest_statistic_record:
            self.latest_statistic_record = CommonStatistic(
                meta={'id': latest_statistic_record['id'], 'index': statistic_index_name},
                **latest_statistic_record)
            if not is_same_time(latest_kdata_timestamp, self.latest_statistic_record['updateTimestamp']):
                self.logger.warning(
                    "latest_kdata_timestamp:{},latest_statistic_timestamp:{}".format(latest_kdata_timestamp,
                                                                                     self.latest_statistic_record[
                                                                                         'updateTimestamp']))
        else:
            self.latest_statistic_record = None

        if latest_kdata_timestamp and self.latest_statistic_record:
            self.start_timestamp = min(latest_kdata_timestamp,
                                       to_timestamp(self.latest_statistic_record['updateTimestamp']))

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

            self.generate_1min_kdata()
            self.generate_eos_daily_statistic()

            self.init_new_computing_interval(event_item['timestamp'])
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
        statistic_doc.save(force=True)

    def generate_eos_daily_statistic(self):
        # ignore the statistic has computed before
        if self.latest_statistic_record and self.kdata_timestamp <= to_timestamp(
                self.latest_statistic_record['updateTimestamp']):
            return

        # update the statistic
        if (not self.latest_statistic_record) or (not is_same_date(self.latest_statistic_record['timestamp'],
                                                                   self.df['timestamp'][0])):
            doc_id = "{}_{}".format(self.security_id, self.last_day_time_str)
            self.latest_statistic_record = CommonStatistic(meta={'id': doc_id, 'index': statistic_index_name},
                                                           id=doc_id,
                                                           timestamp=self.last_day_time_str,
                                                           securityId=self.security_id,
                                                           code=self.security_item['code'],
                                                           name=self.security_item['name'])

        volume = self.df['volume'].sum()
        turnover = self.df['turnover'].sum()
        flow = (self.df['turnover'] * self.df['direction']).sum()

        flowIn = self.df[self.df['direction'] == 1]['turnover'].sum()
        flowOut = self.df[self.df['direction'] == -1]['turnover'].sum()

        bigFlowIn = self.df[(self.df['direction'] == 1) & (self.df['turnover'] >= self.BIG_ORDER)]['turnover'].sum()
        middleFlowIn = self.df[(self.df['direction'] == 1) & (self.df['turnover'] >= self.MIDDLE_ORDER) & (
                self.df['turnover'] < self.BIG_ORDER)]['turnover'].sum()
        smallFlowIn = self.df[(self.df['direction'] == 1) & (self.df['turnover'] < self.MIDDLE_ORDER)]['turnover'].sum()

        bigFlowOut = self.df[(self.df['direction'] == -1) & (self.df['turnover'] >= self.BIG_ORDER)]['turnover'].sum()
        middleFlowOut = self.df[(self.df['direction'] == -1) & (self.df['turnover'] >= self.MIDDLE_ORDER) & (
                self.df['turnover'] < self.BIG_ORDER)]['turnover'].sum()
        smallFlowOut = self.df[(self.df['direction'] == -1) & (self.df['turnover'] < self.MIDDLE_ORDER)][
            'turnover'].sum()

        self.update_statistic_doc(self.latest_statistic_record, {'volume': volume,
                                                                 'turnover': turnover,
                                                                 'flow': flow,
                                                                 'flowIn': flowIn,
                                                                 'flowOut': flowOut,
                                                                 'bigFlowIn': bigFlowIn,
                                                                 'middleFlowIn': middleFlowIn,
                                                                 'smallFlowIn': smallFlowIn,
                                                                 'bigFlowOut': bigFlowOut,
                                                                 'middleFlowOut': middleFlowOut,
                                                                 'smallFlowOut': smallFlowOut
                                                                 }, updateTimestamp=self.last_mirco_time_str)

    def generate_1min_kdata(self):
        doc_id = "{}_{}".format(self.security_id, self.last_mirco_time_str)
        kdata_doc = CommonKData(meta={'id': doc_id, 'index': kdata_index_name}, id=doc_id)
        if kdata_doc.exist(index=kdata_index_name):
            return

        se_price = self.df['price']
        high = se_price.max()
        low = se_price.min()
        open = se_price[0]
        close = se_price[len(se_price) - 1]
        volume = self.df['volume'].sum()
        turnover = self.df['turnover'].sum()

        kdata_json = {
            'id': doc_id,
            'timestamp': self.last_mirco_time_str,
            'updateTimestamp': self.last_mirco_time_str,
            'securityId': self.security_item['id'],
            'code': self.security_item['code'],
            'name': self.security_item['name'],
            'open': float(open),
            'high': float(high),
            'low': float(low),
            'close': float(close),
            'volume': float(volume),
            'turnover': float(turnover)
        }

        fill_doc_type(kdata_doc, kdata_json)

        kdata_doc.save(force=True)


if __name__ == '__main__':
    EosStatisticBot().run()
