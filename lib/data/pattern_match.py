import datetime

import requests


def call_historcial_pattern_match_by_milliseconds(
    symbol,
    start_time_to_match_pattern_timestamp_milliseconds,
    end_time_to_match_pattern_timestamp_milliseconds,
    timeInterval
):
    url = r"https://j32e1smuxe.execute-api.us-east-1.amazonaws.com/prod/api/v1/dynamic-history-match/"
    timeIntervalUpperCase = timeInterval.upper()
    payload = """
    {{
        "endTime": {},
        "startTime": {},
        "symbol": "{}",
        "timeInterval": "{}"
    }}
    """.format(end_time_to_match_pattern_timestamp_milliseconds, start_time_to_match_pattern_timestamp_milliseconds, symbol, timeIntervalUpperCase)
    try:
        response = requests.request("POST", url, data=payload)
    except Exception as e:
        print('error', e)
        return []    
    # convert response to json
    json_response = response.json()
    
    matched_event_array = json_response.get('data', {}).get('eventArray', [])
    
    # e.g. using 100 days to match pattern, then use 50 days to separate each historical events
    MINIMUM_SECONDS_FOR_INDEPENDENT_EVENTS = 0.5 * (end_time_to_match_pattern_timestamp_milliseconds- start_time_to_match_pattern_timestamp_milliseconds)
    
    # if two event's have startDate that are too close, then only keep the earlier happened event
    # startDate is epochTime, to datetimeobject will need datetime.datetime.fromtimestamp(matched_start_date / 1000.0)
    
    sorted_events = sorted(matched_event_array, key=lambda x: x['startDate'])

    # Filtering events
    filtered_events = []
    last_added_event_date = None
    for event in sorted_events:
        event_start_date = event['startDate']

        if last_added_event_date is None or (event_start_date - last_added_event_date) >= MINIMUM_SECONDS_FOR_INDEPENDENT_EVENTS:
            filtered_events.append(event)
            last_added_event_date = event_start_date
    
    return filtered_events



def call_historcial_pattern_match(
    symbol,
    start_time_to_match_pattern,
    end_time_to_match_pattern,
    timeInterval
):    
    # convert from datetime to timestamp
    start_time_to_match_pattern_timestamp = datetime.datetime.strptime(start_time_to_match_pattern, '%Y-%m-%d').timestamp()
    end_time_to_match_pattern_timestamp = datetime.datetime.strptime(end_time_to_match_pattern, '%Y-%m-%d').timestamp()
    
    # convert from timestamp to milliseconds
    start_time_to_match_pattern_timestamp_milliseconds = int(start_time_to_match_pattern_timestamp * 1000)
    end_time_to_match_pattern_timestamp_milliseconds = int(end_time_to_match_pattern_timestamp * 1000)
    return call_historcial_pattern_match_by_milliseconds(
        symbol,
        start_time_to_match_pattern_timestamp_milliseconds,
        end_time_to_match_pattern_timestamp_milliseconds,
        timeInterval
    )
    
    
    
def summarize_matched_event_array(matched_event_array):
    
    top_events_to_consider = 20
    
    # sort by score
    sorted_matched_event_array = sorted(matched_event_array, key=lambda x: x['score'], reverse=True)
    
    # only consider top 20 events
    matched_event_array = sorted_matched_event_array[:top_events_to_consider]
    
    # calculate mean return
    mean_return = 0
    weighted_mean_return = 0 # the later in the event less weighted
    max_return = -float('inf')  # Set to negative infinity for initialization
    min_return = float('inf')  # Set to positive infinity for initialization
    total_weight = 0

    
    for event in matched_event_array:
        matched_event_candles = event['candles']        
        matched_event_datapoints = event['dataPoints']
        closing_values = [candle['c'] for candle in matched_event_candles]
        last_close_in_match_zone = closing_values[matched_event_datapoints-1] # it is a price
        # projected_return_percentage_array is an array that closing_values[matched_event_datapoints:] / last_close_in_match_zone
        
        if last_close_in_match_zone <= 0:
            continue
        projected_return_percentage_array = [ 100*(close -last_close_in_match_zone) / last_close_in_match_zone for close in closing_values[matched_event_datapoints:] ]
        
        event_mean_return = sum(projected_return_percentage_array) / len(projected_return_percentage_array)
        mean_return += event_mean_return

        # Weighted mean calculation (later events less weighted)
        weight = 1
        weighted_mean_return += event_mean_return * weight
        total_weight += weight

        # Update max and min returns
        max_return = max(max_return, max(projected_return_percentage_array, default=max_return))
        min_return = min(min_return, min(projected_return_percentage_array, default=min_return))

    # Finalize mean and weighted mean calculations
    mean_return /= len(matched_event_array)
    weighted_mean_return /= total_weight if total_weight else 1  # Avoid division by zero

    
    return {
        'number_of_events': len(matched_event_array),
        'mean_return': mean_return,
        'weighted_mean_return': weighted_mean_return,
        'max_return': max_return,
        'min_return': min_return
    }