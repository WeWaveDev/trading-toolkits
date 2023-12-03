import datetime
import os

import requests

if __name__ == '__main__':
    url = r"https://j32e1smuxe.execute-api.us-east-1.amazonaws.com/prod/api/v1/dynamic-history-match/"
    start_time_to_match_pattern = '2023-04-01'
    end_time_to_match_pattern = '2023-07-01'
    
    # convert from datetime to timestamp
    start_time_to_match_pattern_timestamp = datetime.datetime.strptime(start_time_to_match_pattern, '%Y-%m-%d').timestamp()
    end_time_to_match_pattern_timestamp = datetime.datetime.strptime(end_time_to_match_pattern, '%Y-%m-%d').timestamp()
    
    # convert from timestamp to milliseconds
    start_time_to_match_pattern_timestamp_milliseconds = int(start_time_to_match_pattern_timestamp * 1000)
    end_time_to_match_pattern_timestamp_milliseconds = int(end_time_to_match_pattern_timestamp * 1000)
    
    payload = payload = """
    {{
        "endTime": {},
        "startTime": {},
        "symbol": "AAPL",
        "timeInterval": "1D"
    }}
    """.format(end_time_to_match_pattern_timestamp_milliseconds, start_time_to_match_pattern_timestamp_milliseconds)

    try:
        response = requests.request("POST", url, data=payload)
    except Exception as e:
        print('error', e)    
    # convert response to json
    json_response = response.json()
    
    matched_event_array = json_response.get('data', {}).get('eventArray', [])
    
    
    # for key, value in json_response['data']:
    #     print(key)

    matched_event_array_top = matched_event_array[:3]

    for index, matched_event in enumerate(matched_event_array_top):
        print('matched event #{}'.format(index))
        matched_start_date = matched_event['startDate']
        matched_end_date = matched_event['endDate']
        matched_score = matched_event['score']
        xToYScale = matched_event['xToYScale']
        xToYOffset = matched_event['xToYOffset']
        matched_event_candles = matched_event['candles']        
        matched_event_datapoints = matched_event['dataPoints']    
                
        matched_start_date_string = datetime.datetime.fromtimestamp(matched_start_date / 1000.0)
        matched_end_date_string = datetime.datetime.fromtimestamp(matched_end_date / 1000.0)
        
        print('matched start date: {}, {} UTC'.format(matched_start_date, matched_start_date_string))
        print('matched end date: {} {} UTC'.format(matched_end_date, matched_end_date_string))
        print('matched score: {}'.format(matched_score))
        
        
        # only print 1 level of json
        for key, value in matched_event.items():
            print(key)

        # print projections
        print('matched_event_datapoints', matched_event_datapoints, len(matched_event_candles))
        print('matched zone index {} to {}'. format(0, matched_event_datapoints-1))
        print('prediction zone index {} to {}'. format(matched_event_datapoints, len(matched_event_candles)-1))
        
        # print the candles
        
        print('\nmatched zone original data')
        for index, candle in enumerate(matched_event_candles[:matched_event_datapoints]):
            print(index, candle.get('t'), candle.get('c'))
        
        print('\nprediction zone original data')
        for index, candle in enumerate(matched_event_candles[matched_event_datapoints:]):
            print(index, candle.get('c'))
        
            
        print('---------------------------------')
            
            
    
    
