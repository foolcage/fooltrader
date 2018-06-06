# -*- coding: utf-8 -*-
import logging
from ast import literal_eval

from elasticsearch_dsl import Index

from fooltrader import es

logger = logging.getLogger(__name__)


def es_get_latest_record(index, time_field='timestamp', query=None):
    body = '''
{
    "query": {
        "match_all": {}
    },
    "size": 1,
    "sort": [
        {
            "timestamp": {
                "order": "desc"
            }
        }
    ]
}
'''
    if time_field != 'timestamp':
        body = body.replace('timestamp', time_field)

    body = literal_eval(body)
    if query:
        body['query'] = query

    try:
        logger.info("search index:{},body:{}".format(index, body))
        response = es.search(index=index, body=body)
        if response['hits']['hits']:
            return response['hits']['hits'][0]['_source']
    except Exception as e:
        logger.warning(e)
    return None


def es_delete(index, query=None):
    if query:
        body = {"query": query}
        es.delete_by_query(index=index, body=body)
    else:
        es.delete(index=index)


def es_index_mapping(index_name, doc_type, force=False):
    # 创建索引
    index = Index(index_name)
    index.doc_type(doc_type)

    if not index.exists():
        index.create()
    else:
        if force:
            index.upgrade()


def es_query_date_range(start_date, end_date, **terms):
    if terms:

        return \
            {
                "query": {
                    "bool": {
                        "must": {
                            "term": terms
                        },
                        "filter": {
                            "range": {
                                "timestamp": {
                                    "gte": start_date,
                                    "lte": end_date
                                }
                            }
                        }
                    }
                }
            }
    else:
        return \
            {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_date,
                            "lte": end_date
                        }
                    }
                }
            }
