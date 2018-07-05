## 订阅
```
curl -XPUT "localhost:5000/subscription" -H 'Content-Type: application/json' -d '{
  "userId": "aaa",
  "securityType": "cryptocurrency",
  "exchange": "kraken",
  "code": "BCH-USD",
  "email": "5533061@qq.com",
  "condition": {
    "upPct": 0.01,
    "downPct": -0.02,
    "up": 7000,
    "down": 6000,
    "cross": 0.02
  },
  "repeat": false
}'

{
  "code": 0,
  "msg": "success",
  "payload": {
    "_id": "bf1SaWQBfBeKI-v8T-EK",
    "_index": "subscription",
    "_source": {
      "code": "BCH-USD",
      "condition": {
        "cross": 0.02,
        "down": 6000,
        "downPct": -0.02,
        "up": 7000,
        "upPct": 0.01
      },
      "email": "5533061@qq.com",
      "exchange": "kraken",
      "repeat": false,
      "securityType": "cryptocurrency",
      "userId": "aaa"
    },
    "_type": "doc",
    "_version": 1
  }
}
```
## 查询
curl -XGET "localhost:5000/subscription?userId=aaa"                               
```
{
  "code": 0,
  "msg": "success",
  "payload": {
    "hits": [
      {
        "_id": "af1jZGQBfBeKI-v8aeFw",
        "_index": "subscription",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USD",
          "condition": {
            "cross": 0.02,
            "down": 6000,
            "downPct": -0.02,
            "up": 7000,
            "upPct": 0.01
          },
          "email": "5533061@qq.com",
          "exchange": "kraken",
          "repeat": false,
          "securityType": "cryptocurrency",
          "userId": "aaa"
        },
        "_type": "doc"
      },
      {
        "_id": "Zf1aZGQBfBeKI-v8buGQ",
        "_index": "subscription",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USD",
          "condition": {
            "cross": 0.02,
            "down": 6000,
            "downPct": -0.02,
            "up": 7000,
            "upPct": 0.01
          },
          "email": "5533061@qq.com",
          "exchange": "kraken",
          "repeat": false,
          "securityType": "cryptocurrency",
          "userId": "aaa"
        },
        "_type": "doc"
      },
      {
        "_id": "aP1iZGQBfBeKI-v8AeHP",
        "_index": "subscription",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USD",
          "condition": {
            "cross": 0.02,
            "down": 6000,
            "downPct": -0.02,
            "up": 7000,
            "upPct": 0.01
          },
          "email": "5533061@qq.com",
          "exchange": "kraken",
          "repeat": false,
          "securityType": "cryptocurrency",
          "userId": "aaa"
        },
        "_type": "doc"
      },
      {
        "_id": "bf1SaWQBfBeKI-v8T-EK",
        "_index": "subscription",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USD",
          "condition": {
            "cross": 0.02,
            "down": 6000,
            "downPct": -0.02,
            "up": 7000,
            "upPct": 0.01
          },
          "email": "5533061@qq.com",
          "exchange": "kraken",
          "repeat": false,
          "securityType": "cryptocurrency",
          "userId": "aaa"
        },
        "_type": "doc"
      }
    ],
    "max_score": 0.0,
    "total": 4
  }
}
```
## 更新
```
curl -XPUT "localhost:5000/subscription/bf1SaWQBfBeKI-v8T-EK" -H 'Content-Type: application/json' -d '{
  "userId": "aaa",
  "securityType": "cryptocurrency",
  "exchange": "kraken",
  "code": "BTC-USD",
  "email": "5533061@qq.com",
  "condition": {
    "upPct": 0.01,
    "downPct": -0.02,
    "up": 7000,
    "down": 6000,
    "cross": 0.02
  },
  "repeat": false
}'
{
  "code": 0,
  "msg": "success",
  "payload": {
    "_id": "bf1SaWQBfBeKI-v8T-EK",
    "_index": "subscription",
    "_source": {
      "code": "BTC-USD",
      "condition": {
        "cross": 0.02,
        "down": 6000,
        "downPct": -0.02,
        "up": 7000,
        "upPct": 0.01
      },
      "email": "5533061@qq.com",
      "exchange": "kraken",
      "repeat": false,
      "securityType": "cryptocurrency",
      "userId": "aaa"
    },
    "_type": "doc",
    "_version": 2
  }
}
```
