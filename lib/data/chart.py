import datetime
import json

import pandas as pd
import requests


def get_symbol_chart(symbol, time_interval, start_date, end_date):
    url = "https://7cgz3z2htj.execute-api.us-east-1.amazonaws.com/snapshot-prod/api/v1/get-chart-data-with-start-end"

    # Building the payload
    payload = {
        "symbol": symbol,
        "timeInterval": time_interval.lower(), # small case
        "startDate": start_date, # take milliseconds of UTC epoch time
        "endDate": end_date  # take milliseconds of UTC epoch time
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


def get_ohlc_history_in_dataframe(
    symbol, time_interval, start_date, end_date):
    
    data_array = get_symbol_chart(symbol, time_interval, start_date, end_date)
    
    # Prepare lists for each column
    dates, opens, highs, lows, closes, volumes = [], [], [], [], [], []

    for data_point in data_array:
        # Convert timestamp to datetime and format it
        date = datetime.datetime.utcfromtimestamp(data_point['t'] / 1000.0).strftime('%Y-%m-%d')
        
        # Append data to respective lists
        dates.append(date)
        opens.append(data_point['o'])
        highs.append(data_point['h'])
        lows.append(data_point['l'])
        closes.append(data_point['c'])
        volumes.append(data_point['v'])

    # Create a DataFrame
    df = pd.DataFrame({
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    }, index=pd.to_datetime(dates))

    return df
    