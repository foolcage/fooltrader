import json
import os

from fooltrader.contract.files_contract import get_forecast_event_path


def get_forecast_items(security_item):
    forecast_path = get_forecast_event_path(security_item)
    if os.path.exists(forecast_path):
        with open(forecast_path) as data_file:
            forecast_json = json.load(data_file)
            for json_item in reversed(forecast_json):
                yield json_item
