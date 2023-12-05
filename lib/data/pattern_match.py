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