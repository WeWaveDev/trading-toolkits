import datetime
import json
from zoneinfo import ZoneInfo

import requests

utc=ZoneInfo('UTC')
eastern = ZoneInfo('America/New_York')


def filter_out_pre_after_us_stock_market(json_object):
    # Use a list comprehension to filter out unwanted times
    filtered_json = []
    for obj in json_object:
        # Convert timestamp to Eastern Time
        utc_timestamp = datetime.datetime.utcfromtimestamp(obj['t'] / 1000.0)
        utc_timestamp = utc_timestamp.replace(tzinfo=utc)
        eastern_dt = utc_timestamp.astimezone(eastern)
        hour = eastern_dt.hour
        minute = eastern_dt.minute

        # Check if the time is between 9:30 AM and 4:00 PM EST
        if (hour > 9 or (hour == 9 and minute >= 30)) and hour < 16:
            filtered_json.append(obj)

    return filtered_json

def print_pretty(json_object):
    # print the first and last 3 objects
    print('first 3 objects')
    for index, object in enumerate(json_object[:3]):
        utc_timestamp_string = datetime.datetime.utcfromtimestamp(object['t'] / 1000.0)
        print('open: {}'.format(object['o']))
        print('high: {}'.format(object['h']))
        print('low: {}'.format(object['l']))
        print('close: {}'.format(object['c']))
        print('volume: {}'.format(object['v']))
        print('timestamp: {}'.format(object['t']))
        print('timestamp string: {} (UTC)'.format(utc_timestamp_string))
        print('')
        
    print('last 3 objects')
    for index, object in enumerate(json_object[-3:]):
        utc_timestamp_string = datetime.datetime.utcfromtimestamp(object['t'] / 1000.0)
        print('open: {}'.format(object['o']))
        print('high: {}'.format(object['h']))
        print('low: {}'.format(object['l']))
        print('close: {}'.format(object['c']))
        print('volume: {}'.format(object['v']))
        print('timestamp: {}'.format(object['t']))
        print('timestamp string: {} (UTC)'.format(utc_timestamp_string))
        print('')
    
    # print length
    print('length: {}'.format(len(json_object)))


def convert_date_to_timestamp(date_string, date_format="%Y-%m-%d"):
    date = datetime.datetime.strptime(date_string, date_format) # TODO: UTC
    return int(date.timestamp() * 1000)

convert_date_to_utc_timestamp = convert_date_to_timestamp

# def convert_date_to_utc_timestamp(date_string, date_format="%Y-%m-%d"):
#     # Parse the date string into a naive datetime object
#     naive_datetime = datetime.datetime.strptime(date_string, date_format)
    
#     # Assume the naive datetime is in the local time zone
#     local_timezone = datetime.datetime.now().astimezone().tzinfo
#     local_datetime = naive_datetime.replace(tzinfo=local_timezone)
    
#     # Convert the datetime to UTC
#     utc_datetime = local_datetime.astimezone(ZoneInfo("UTC"))

#     # Convert the UTC datetime to a timestamp (in seconds)
#     utc_timestamp = int(utc_datetime.timestamp()*1000)

#     return utc_timestamp

# def convert_date_to_utc_timestamp(date_string, date_format="%Y-%m-%d"):
#     # Create a timezone-aware datetime object
#     local = pytz.timezone("UTC")
#     naive_date = datetime.datetime.strptime(date_string, date_format)
#     local_dt = local.localize(naive_date, is_dst=None)
#     # Convert to UTC
#     utc_dt = local_dt.astimezone(pytz.utc)
#     # Convert to timestamp in milliseconds
#     return int(utc_dt.timestamp() * 1000)

# def convert_date_to_est_timestamp(date_string, date_format="%Y-%m-%d"):
#     # Create a timezone-aware datetime object
#     local = pytz.timezone("US/Eastern")
#     naive_date = datetime.datetime.strptime(date_string, date_format)
#     local_dt = local.localize(naive_date, is_dst=None)
#     # Convert to EST
#     est_dt = local_dt.astimezone(pytz.timezone("US/Eastern"))
#     # Convert to timestamp in milliseconds
#     return int(est_dt.timestamp() * 1000)

def get_symbol_chart(symbol, time_interval, start_date, end_date):
    url = "https://7cgz3z2htj.execute-api.us-east-1.amazonaws.com/snapshot-prod/api/v1/get-chart-data-with-start-end"

    # Building the payload
    payload = {
        "symbol": symbol,
        "timeInterval": time_interval,
        "startDate": start_date,
        "endDate": end_date
    }

    print('payload')
    print(payload)

    try:
      # Sending the request
        response = requests.post(url, headers={}, data=json.dumps(payload))
    except Exception as e:
        print('error', e)    
    # convert response to json
    json_response = response.json()
    return json_response.get('data', [])

def _run_1day_interval_example():
    # intraday 1 day
    start_date = convert_date_to_timestamp("2023-06-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
    end_date = convert_date_to_timestamp("2023-06-01T23:59:59", '%Y-%m-%dT%H:%M:%S')
    data_array = get_symbol_chart("AAPL", "1d", start_date, end_date)
    print_pretty(data_array)

def _run_5min_interval_example():
    # intraday 5 min
    start_date = convert_date_to_timestamp("2023-06-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
    end_date = convert_date_to_timestamp("2023-06-01T23:59:59", '%Y-%m-%dT%H:%M:%S')
    data_array = get_symbol_chart("AAPL", "5min", start_date, end_date)
    print_pretty(data_array)
    
def _run_5min_interval_excluding_pre_after_market_example():
    # intraday 5 min
    start_date = convert_date_to_utc_timestamp("2023-06-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
    end_date = convert_date_to_utc_timestamp("2023-06-01T23:59:59", '%Y-%m-%dT%H:%M:%S')
    data_array = get_symbol_chart("AAPL", "5min", start_date, end_date)
    filtered_data_array = filter_out_pre_after_us_stock_market(data_array)
    print_pretty(filtered_data_array)
  
if __name__ == "__main__":
    # _run_1day_interval_example()
    # _run_5min_interval_example()
    _run_5min_interval_excluding_pre_after_market_example()

