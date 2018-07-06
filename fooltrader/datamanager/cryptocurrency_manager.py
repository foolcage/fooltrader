# -*- coding: utf-8 -*-
import argparse

from fooltrader.connector.kafka_connector import cryptocurrency_tick_to_kafka

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('exchange', help='the exchange to crawl')
    parser.add_argument('--pairs', help='the pair list')

    args = parser.parse_args()

    cryptocurrency_tick_to_kafka(exchange=args.exchange)
