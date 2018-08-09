# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import elasticsearch.helpers
from pymongo import MongoClient

from fooltrader import fill_doc_type, es_client
from fooltrader.domain.data.es_quote import EosAccount
from fooltrader.settings import EOS_MONGODB_URL
from fooltrader.utils.es_utils import es_index_mapping
from fooltrader.utils.utils import to_time_str

logger = logging.getLogger(__name__)

client = MongoClient(EOS_MONGODB_URL)

db = client['eosMain']
db_rs = client['local']

es_index_mapping("eos_account", EosAccount)


def eos_acount_update_to_es():
    pass

def eos_account_to_es():
    account = db.accounts
    count = account.count()

    logger.info("current account size:{}".format(count))

    actions = []

    # {
    #     "_id": ObjectId("5b6651aa30cafb28be710275"),
    #     "name": "eosio.ram",
    #     "create_time": ISODate("2018-06-09T11:57:39.000Z"),
    #     "liquid_eos": NumberLong(26757051448),
    #     "stacked_eos": NumberLong(0),
    #     "total_eos": NumberLong(26757051448),
    #     "unstacking_eos": NumberLong(0)
    # }
    start = 0
    size = 1000
    while True:
        for item in account.find().skip(start).limit(size):
            liquidEos = item.get('liquid_eos', 0)
            stackedEos = item.get('stacked_eos', 0)
            unstackingEos = item.get('unstacking_eos', 0)
            totalEos = item.get('total_eos', 0)
            createTime = item.get('create_time', datetime.now())
            json_item = {
                "id": str(item["_id"]),
                "userId": item["name"],
                "liquidEos": liquidEos,
                "stackedEos": stackedEos,
                "totalEos": totalEos,
                "unstackingEos": unstackingEos,
                "timestamp": to_time_str(createTime),
                "updateTimestamp": to_time_str(datetime.now())
            }
            eos_account = EosAccount(meta={'id': json_item['id'], 'index': "eos_account"})
            fill_doc_type(eos_account, json_item)

            actions.append(eos_account.to_dict(include_meta=True))

        if actions:
            resp = elasticsearch.helpers.bulk(es_client, actions)
            logger.info("index to {} success:{} failed:{}".format("eos_account", resp[0], len(resp[1])))
            if resp[1]:
                logger.error("index to {} error:{}".format("eos_account", resp[1]))

        if len(actions) < size:
            break
        actions = []

        start += (size - 1)


if __name__ == '__main__':
    eos_account_to_es()
