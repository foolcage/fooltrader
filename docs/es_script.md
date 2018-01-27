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

curl -XPOST 'localhost:9200/income_statement/doc/_search?pretty&filter_path=hits.hits._source' -H 'Content-Type: application/json' -d'
{
  "query": {
    "range" : {
                "reportDate" : {
                    "gte" : "20170630",
                    "lte" :  "20170630"
                }
            }
  },
  "size": 10,
  "sort": [
    {
      "netProfit": {
        "order": "desc"
      }
    }
  ]
}
'
```
