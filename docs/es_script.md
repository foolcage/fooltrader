```bash
bin/elasticsearch-plugin install file:///home/xuanqi/software/x-pack-6.1.1.zip
bin/kibana-plugin install file:///home/xuanqi/software/x-pack-6.1.1.zip
ES_JAVA_OPTS="-Xms8g -Xmx8g"  ./bin/elasticsearch

curl -XPOST 'localhost:9200/index_sh_000001_day_kdata/doc/_search?pretty' -H 'Content-Type: application/json' -d'
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
'

curl -XPOST 'localhost:9200/balance_sheet/doc/_search?pretty' -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": { "securityId" : "stock_sz_000002" }
  },
  "size": 1,
  "sort": [
    {
      "reportDate": {
        "order": "desc"
      }
    }
  ]
}
'
```
