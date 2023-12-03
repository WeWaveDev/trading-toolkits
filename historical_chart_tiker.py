import datetime
import json

import requests


def print_pretty(json_object):
    # each object is {'o': 65.22000594562735, 'h': 66.384213983644, 'l': 65.10796918883077, 'c': 66.1163, 'v': 137310400, 't': 1576108800000},
    
    # print the first and last 3 objects
    print('first 3 objects')
    for index, object in enumerate(json_object[:3]):
        timestamp_string = datetime.datetime.fromtimestamp(object['t'] / 1000.0)
        print('open: {}'.format(object['o']))
        print('high: {}'.format(object['h']))
        print('low: {}'.format(object['l']))
        print('close: {}'.format(object['c']))
        print('volume: {}'.format(object['v']))
        print('timestamp: {}'.format(object['t']))
        print('timestamp string: {}'.format(timestamp_string))
        print('')
        
    print('last 3 objects')
    for index, object in enumerate(json_object[-3:]):
        timestamp_string = datetime.datetime.fromtimestamp(object['t'] / 1000.0)
        print('open: {}'.format(object['o']))
        print('high: {}'.format(object['h']))
        print('low: {}'.format(object['l']))
        print('close: {}'.format(object['c']))
        print('volume: {}'.format(object['v']))
        print('timestamp: {}'.format(object['t']))
        print('timestamp string: {}'.format(timestamp_string))
        print('')
    
    # print length
    print('length: {}'.format(len(json_object)))


def convert_date_to_timestamp(date_string):
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return int(date.timestamp() * 1000)

def get_symbol_chart(symbol, time_interval, start_date=None, end_date=None):
    url = "https://7cgz3z2htj.execute-api.us-east-1.amazonaws.com/snapshot-prod/api/v1/get-chart-data-with-start-end"

    # Building the payload
    payload = {
        "symbol": symbol,
        "timeInterval": time_interval,
    }

    # Adding optional dates if provided
    if start_date is not None:
        payload["startDate"] = convert_date_to_timestamp(start_date)
    if end_date is not None:
        payload["endDate"] = convert_date_to_timestamp(end_date)

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
  
  
# Example usage
response_text = get_symbol_chart("AAPL", "1d", "2023-01-01", "2023-06-30")
print_pretty(response_text)


