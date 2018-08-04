## 获取支持的数字货币
```
curl 'http://localhost:5000/security?securityType=cryptocurrency'                 
{
  "code": 0,
  "msg": "success",
  "payload": {
    "hits": [
      {
        "_id": "cryptocurrency_binance_EOS-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "EOS-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_EOS-USDT",
          "name": "EOS/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_bitfinex_BTC-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "BTC-USDT",
          "exchange": "bitfinex",
          "id": "cryptocurrency_bitfinex_BTC-USDT",
          "name": "BTC/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_bitfinex_EOS-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "EOS-USDT",
          "exchange": "bitfinex",
          "id": "cryptocurrency_bitfinex_EOS-USDT",
          "name": "EOS/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_bitfinex_BCH-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USDT",
          "exchange": "bitfinex",
          "id": "cryptocurrency_bitfinex_BCH-USDT",
          "name": "BCH/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_binance_BTC-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "BTC-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_BTC-USDT",
          "name": "BTC/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_huobipro_EOS-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "EOS-USDT",
          "exchange": "huobipro",
          "id": "cryptocurrency_huobipro_EOS-USDT",
          "name": "EOS/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_bitfinex_ETH-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "ETH-USDT",
          "exchange": "bitfinex",
          "id": "cryptocurrency_bitfinex_ETH-USDT",
          "name": "ETH/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_binance_ETH-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "ETH-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_ETH-USDT",
          "name": "ETH/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_huobipro_BCH-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USDT",
          "exchange": "huobipro",
          "id": "cryptocurrency_huobipro_BCH-USDT",
          "name": "BCH/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_huobipro_XRP-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "XRP-USDT",
          "exchange": "huobipro",
          "id": "cryptocurrency_huobipro_XRP-USDT",
          "name": "XRP/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      }
    ],
    "max_score": 0.0,
    "total": 15
  }
}
```

## 指定交易所
```
curl 'http://localhost:5000/security?securityType=cryptocurrency&exchange=binance'
{
  "code": 0,
  "msg": "success",
  "payload": {
    "hits": [
      {
        "_id": "cryptocurrency_binance_EOS-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "EOS-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_EOS-USDT",
          "name": "EOS/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_binance_BTC-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "BTC-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_BTC-USDT",
          "name": "BTC/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_binance_ETH-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "ETH-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_ETH-USDT",
          "name": "ETH/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_binance_BCH-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "BCH-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_BCH-USDT",
          "name": "BCH/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      },
      {
        "_id": "cryptocurrency_binance_XRP-USDT",
        "_index": "crypto_currency_meta",
        "_score": 0.0,
        "_source": {
          "code": "XRP-USDT",
          "exchange": "binance",
          "id": "cryptocurrency_binance_XRP-USDT",
          "name": "XRP/USDT",
          "type": "cryptocurrency"
        },
        "_type": "doc"
      }
    ],
    "max_score": 0.0,
    "total": 5
  }
}

```

## 订阅
```
curl -XPUT "localhost:5000/subscription" -H 'Content-Type: application/json' -d '{
            "userId": "oRvNP0XIb9G3g6a-2fAX9RHX5--Q",
            "securityType": "cryptocurrency",
            "exchange": "contract",
            "code": "RAM-EOS",
            "upPct": 0.02,
            "downPct": -0.02,
            "upTo": 1000,
            "downTo": 900,
            "actions": ["weixin"],
            "repeat": false
        }'
{
  "code": 0,
  "msg": "success",
  "payload": {
    "_id": "FPWGfWQB7OYj2Pz1vY8U",
    "_index": "price_subscription",
    "_source": {
      "actions": [
        "weixin",
        "email",
        "shortMsg"
      ],
      "code": "XRP-USDT",
      "down": 6700,
      "downPct": -0.02,
      "exchange": "binance",
      "repeat": false,
      "securityType": "cryptocurrency",
      "type": "price",
      "up": 6500,
      "upPct": 0.02,
      "userId": "oRvNP0XIb9G3g6a-2fAX9RHX5--Q"
    },
    "_type": "doc",
    "_version": 1
  }
}

```

## 更新
```
curl -XPUT "localhost:5000/subscription/FPWGfWQB7OYj2Pz1vY8U" -H 'Content-Type: application/json' -d '{
            "userId": "oRvNP0XIb9G3g6a-2fAX9RHX5--Q",
            "type": "price",
            "securityType": "cryptocurrency",
            "exchange": "binance",
            "code": "XRP-USDT",
            "upPct": 0.05,
            "downPct": -0.02,
            "up": 6500,
            "down": 6700,
            "actions": ["weixin", "email", "shortMsg"],
            "repeat": false
        }'
{
  "code": 0,
  "msg": "success",
  "payload": {
    "_id": "FPWGfWQB7OYj2Pz1vY8U",
    "_index": "price_subscription",
    "_source": {
      "actions": [
        "weixin",
        "email",
        "shortMsg"
      ],
      "code": "XRP-USDT",
      "down": 6700,
      "downPct": -0.02,
      "exchange": "binance",
      "repeat": false,
      "securityType": "cryptocurrency",
      "type": "price",
      "up": 6500,
      "upPct": 0.05,
      "userId": "oRvNP0XIb9G3g6a-2fAX9RHX5--Q"
    },
    "_type": "doc",
    "_version": 2
  }
}
```
## 查询
```
curl -XGET "localhost:5000/subscription?userId=oRvNP0XIb9G3g6a-2fAX9RHX5--Q"      
{
  "code": 0,
  "msg": "success",
  "payload": {
    "hits": [
      {
        "_id": "FPWGfWQB7OYj2Pz1vY8U",
        "_index": "price_subscription",
        "_score": 0.0,
        "_source": {
          "actions": [
            "weixin",
            "email",
            "shortMsg"
          ],
          "code": "XRP-USDT",
          "down": 6700,
          "downPct": -0.02,
          "exchange": "binance",
          "repeat": false,
          "securityType": "cryptocurrency",
          "type": "price",
          "up": 6500,
          "upPct": 0.05,
          "userId": "oRvNP0XIb9G3g6a-2fAX9RHX5--Q"
        },
        "_type": "doc"
      },
      {
        "_id": "FfWLfWQB7OYj2Pz1q4-n",
        "_index": "price_subscription",
        "_score": 0.0,
        "_source": {
          "actions": [
            "weixin",
            "email",
            "shortMsg"
          ],
          "code": "BTC-USDT",
          "down": 6700,
          "downPct": -0.02,
          "exchange": "binance",
          "repeat": false,
          "securityType": "cryptocurrency",
          "type": "price",
          "up": 6500,
          "upPct": 0.02,
          "userId": "oRvNP0XIb9G3g6a-2fAX9RHX5--Q"
        },
        "_type": "doc"
      }
    ],
    "max_score": 0.0,
    "total": 2
  }
}
```
