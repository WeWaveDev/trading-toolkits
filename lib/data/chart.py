import json

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