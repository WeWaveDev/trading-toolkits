import datetime
import json
from zoneinfo import ZoneInfo

# import pytz
import requests

utc=ZoneInfo('UTC')

# def filter_out_pre_after_market(json_object):
#     utc = pytz.utc
#     eastern = pytz.timezone('US/Eastern')
    
#     # for each object, check if the timestamp is between 9:30am and 4pm EST. The timestamp is in UTC, so we need to convert it to EST
#     for index, object in enumerate(json_object):
#         utc_timestamp_string = datetime.datetime.utcfromtimestamp(object['t'] / 1000.0)
#         eastern_dt = utc.localize(utc_timestamp_string).astimezone(eastern)
#         hour = eastern_dt.hour
#         minute = eastern_dt.minute
#         if hour < 9 or hour > 16:
#             json_object.pop(index)
#         elif hour == 9 and minute < 30:
#             json_object.pop(index)
            
#     return json_object


fmt = '%Y-%m-%d %H:%M:%S %Z%z'


def filter_out_pre_after_market(json_object):
    # eastern = pytz.timezone('US/Eastern')
    eastern = ZoneInfo('America/New_York')

    # Use a list comprehension to filter out unwanted times
    filtered_json = []
    for obj in json_object:
        # Convert timestamp to Eastern Time
        utc_timestamp = datetime.datetime.utcfromtimestamp(obj['t'] / 1000.0)
        utc_timestamp = utc_timestamp.replace(tzinfo=utc)
        eastern_dt = utc_timestamp.astimezone(eastern)
        print('utc_timestamp.strftime', utc_timestamp.strftime(fmt))

        print('eastern_dt.strftime', eastern_dt.strftime(fmt))
        print('eastern_dt: {}, {} {}. {} {}'.format(eastern_dt, eastern_dt.hour, eastern_dt.minute, obj['t'], utc_timestamp))

        hour = eastern_dt.hour
        minute = eastern_dt.minute

        # Check if the time is between 9:30 AM and 4:00 PM EST
        if (hour > 9 or (hour == 9 and minute >= 30)) and hour < 16:
            filtered_json.append(obj)

    return filtered_json

def print_pretty(json_object):
    # each object is {'o': 65.22000594562735, 'h': 66.384213983644, 'l': 65.10796918883077, 'c': 66.1163, 'v': 137310400, 't': 1576108800000},
    
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

    # # Adding optional dates if provided
    # if start_date is not None:
    #     payload["startDate"] = 
    # if end_date is not None:
    #     payload["endDate"] = convert_date_to_timestamp(end_date)

    print('payload')
    print(payload)

    try:
      # Sending the request
        response = requests.post(url, headers={}, data=json.dumps(payload))
        # print('response')
        # print(response)
    
    except Exception as e:
        print('error', e)    
    # convert response to json
    json_response = response.json()
    
    # print('json_response')
    # print(json_response)
    
    # if {'data': {'MARKET': []} } exists, return array 
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
    filtered_data_array = filter_out_pre_after_market(data_array)
    print_pretty(filtered_data_array)
  
if __name__ == "__main__":
    # _run_1day_interval_example()
    # _run_5min_interval_example()
    _run_5min_interval_excluding_pre_after_market_example()


# response_text = get_symbol_chart("AAPL", "5min", "2023-11-01", "2023-11-01")
# print_pretty(response_text)
