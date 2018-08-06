# -*- coding: utf-8 -*-
from datetime import timedelta

import pandas as pd

from fooltrader.bot.bot import NotifyEventBot
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_statistic_index, \
    get_cryptocurrency_user_statistic
from fooltrader.domain.data.es_quote import CommonKData, CommonStatistic, EosUserStatistic
from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.es_utils import es_get_latest_timestamp, es_get_latest_record, es_index_mapping
from fooltrader.utils.utils import to_timestamp, to_time_str, fill_doc_type, is_same_date, is_same_time

statistic_index_name = get_es_statistic_index(security_type='cryptocurrency', exchange='contract')
user_statistic_index_name = get_cryptocurrency_user_statistic()
kdata_index_name = get_es_kdata_index(security_type='cryptocurrency', exchange='contract', level='1min')

es_index_mapping(statistic_index_name, CommonStatistic)
es_index_mapping(user_statistic_index_name, EosUserStatistic)
es_index_mapping(kdata_index_name, CommonKData)


class StatisticBot(NotifyEventBot):
    BIG_ORDER = 2000
    MIDDLE_ORDER = 500

    def on_init(self):
        super().on_init()
        self.security_id = 'cryptocurrency_contract_RAM-EOS'

        query = {
            "term": {"securityId": ""}
        }
        query["term"]["securityId"] = self.security_id

        # get latest kdata timestamp
        latest_kdata_timestamp = es_get_latest_timestamp(index=kdata_index_name, query=query)

        # get latest statistic timestamp
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

        # get latest user statistic timestamp
        user_statistic_index_name = get_cryptocurrency_user_statistic()
        latest_eos_user_statistic_record = es_get_latest_record(index=user_statistic_index_name,
                                                                query=query, time_field='updateTimestamp')

        if latest_eos_user_statistic_record:
            self.latest_eos_user_statistic_record = EosUserStatistic(
                meta={'id': latest_eos_user_statistic_record['id'], 'index': user_statistic_index_name},
                **latest_eos_user_statistic_record)

            if not is_same_time(latest_kdata_timestamp, self.latest_eos_user_statistic_record['updateTimestamp']):
                self.logger.warning(
                    "latest_kdata_timestamp:{},latest_eos_user_statistic_timestamp:{}".format(latest_kdata_timestamp,
                                                                                              self.latest_statistic_record[
                                                                                                  'updateTimestamp']))
        else:
            self.latest_eos_user_statistic_record = None

        if latest_kdata_timestamp and self.latest_eos_user_statistic_record and self.latest_eos_user_statistic_record:
            self.start_timestamp = min(latest_kdata_timestamp,
                                       to_timestamp(self.latest_eos_user_statistic_record['updateTimestamp']),
                                       to_timestamp(self.latest_eos_user_statistic_record['updateTimestamp']))

    def after_init(self):
        super().after_init()
        if not self.start_timestamp:
            self.start_timestamp = to_timestamp(self.security_item['listDate'])
        self.last_timestamp = None
        self.df = pd.DataFrame()

    def on_event(self, event_item):
        if not self.last_timestamp:
            self.last_timestamp = to_timestamp(event_item['timestamp'])

        current_timestamp = to_timestamp(event_item['timestamp'])

        # calculating last minute
        if current_timestamp.minute != self.last_timestamp.minute:
            self.df.fillna(0, inplace=True)
            self.generate_kdata()
            self.generate_statistic()

            self.last_timestamp = current_timestamp
            self.df = pd.DataFrame()

        self.df = self.df.append(event_item, ignore_index=True)

    # class CommonStatistic(BaseDocType):
    #     id = Keyword()
    #     timestamp = Date()
    #     securityId = Keyword()
    #     code = Keyword()
    #     name = Keyword()
    #
    #     volume = Float()
    #     turnover = Float()
    #     flow = Float()
    #     flowIn = Float()
    #     flowOut = Float()
    #     bigFlowIn = Float()
    #     middleFlowIn = Float()
    #     smallFlowIn = Float()
    #     bigFlowOut = Float()
    #     middleFlowOut = Float()
    #     smallFlowOut = Float()
    #
    #     class Meta:
    #         doc_type = 'doc'
    #         all = MetaField(enabled=False)
    #         dynamic = MetaField('strict')

    def update_statistic_doc(self, append_record, updateTimestamp):
        for key in append_record.keys():
            if pd.isna(append_record[key]):
                the_value = 0
            else:
                the_value = append_record[key]

            if (key in self.latest_statistic_record) and (self.latest_statistic_record[key] != 0):
                self.latest_statistic_record[key] += the_value
            else:
                self.latest_statistic_record[key] = the_value
        self.latest_statistic_record['updateTimestamp'] = updateTimestamp
        self.latest_statistic_record.save(force=True)

    def generate_statistic(self):
        kdata_timestamp = self.last_timestamp + timedelta(seconds=-self.last_timestamp.second,
                                                          microseconds=-self.last_timestamp.microsecond)

        if self.latest_statistic_record and kdata_timestamp < to_timestamp(
                self.latest_statistic_record['updateTimestamp']):
            return

        # update the statistic
        if (not self.latest_statistic_record) or (not is_same_date(self.latest_statistic_record['timestamp'],
                                                                   self.df['timestamp'][0])):
            timestamp = to_time_str(self.last_timestamp)
            doc_id = "{}_{}".format(self.security_id, timestamp)
            self.latest_statistic_record = CommonStatistic(meta={'id': doc_id, 'index': statistic_index_name},
                                                           id=doc_id,
                                                           timestamp=timestamp,
                                                           securityId=self.security_id,
                                                           code=self.security_item['code'],
                                                           name=self.security_item['name'])

        volume = self.df['volume'].sum()
        turnover = self.df['turnover'].sum()
        flow = (self.df['turnover'] * self.df['direction']).sum()

        flowIn = self.df[self.df['direction'] == 1]['volume'].sum()
        flowOut = self.df[self.df['direction'] == -1]['volume'].sum()

        bigFlowIn = self.df[(self.df['direction'] == 1) & (self.df['volume'] >= self.BIG_ORDER)]['volume'].sum()
        middleFlowIn = self.df[(self.df['direction'] == 1) & (self.df['volume'] >= self.MIDDLE_ORDER) & (
                self.df['volume'] < self.BIG_ORDER)]['volume'].sum()
        smallFlowIn = self.df[(self.df['direction'] == 1) & (self.df['volume'] < self.MIDDLE_ORDER)]['volume'].sum()

        bigFlowOut = self.df[(self.df['direction'] == -1) & (self.df['volume'] >= self.BIG_ORDER)]['volume'].sum()
        middleFlowOut = self.df[(self.df['direction'] == -1) & (self.df['volume'] >= self.MIDDLE_ORDER) & (
                self.df['volume'] < self.BIG_ORDER)]['volume'].sum()
        smallFlowOut = self.df[(self.df['direction'] == -1) & (self.df['volume'] < self.MIDDLE_ORDER)][
            'volume'].sum()

        time_str = to_time_str(kdata_timestamp, time_fmt=TIME_FORMAT_MICRO)

        self.update_statistic_doc({
            'volume': volume,
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
        }, updateTimestamp=time_str)

    def generate_kdata(self):
        se_price = self.df['price']
        high = se_price.max()
        low = se_price.min()
        open = se_price[0]
        close = se_price[len(se_price) - 1]
        volume = self.df['volume'].sum()
        turnover = self.df['turnover'].sum()

        kdata_timestamp = self.last_timestamp + timedelta(seconds=-self.last_timestamp.second,
                                                          microseconds=-self.last_timestamp.microsecond)
        time_str = to_time_str(kdata_timestamp, time_fmt=TIME_FORMAT_MICRO)
        doc_id = "{}_{}".format(self.security_id, time_str)
        kdata_json = {
            'id': doc_id,
            'timestamp': time_str,
            'updateTimestamp': time_str,
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

        kdata_doc = CommonKData(meta={'id': doc_id, 'index': kdata_index_name})

        fill_doc_type(kdata_doc, kdata_json)

        kdata_doc.save(force=True)


if __name__ == '__main__':
    StatisticBot().run()
