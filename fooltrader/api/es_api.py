from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Bool

client = Elasticsearch()


def es_get_security_meta(security_type='stock', exchange=['sh', 'sz'], code=None, security_id=None, listDate=None):
    if security_type == 'stock':
        s = Search(using=client, index='stock_meta', extra={"size": 5000, "from_": 0})

        if type(exchange) == list:
            q = Q("term", exchange=exchange[0])
            for ex in exchange[1:]:
                q = Q("term", exchange=ex) | q
        else:
            q = Q("term", exchange=exchange)
        s = s.filter(Bool(q))
        response = s.execute()
        print('Total %d hits found.' % response.hits.total)
        for h in response:
            print(h)


if __name__ == '__main__':
    print(es_get_security_meta())
