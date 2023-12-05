import datetime
import json
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import pandas as pd

from lib.data.chart import get_symbol_chart

utc=ZoneInfo('UTC')
eastern = ZoneInfo('America/New_York')

'''
NOTE: US stock market is open from 9:30 AM to 4:00 PM EST. 
If you only want to get the data during the market hours, you can use the following function to filter out the data outside of the market hours.
Please note that timezone is important here. The API takes and returns the timestamp in UTC timezone.
'''

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

def plot_chart_with_volume(data):
    # Create DataFrame
    df = pd.DataFrame(data)
    # print(df)
    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Convert Unix timestamp to readable date
    df.index = df.index.strftime('%Y-%m-%d %H:%M:%S')

    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plotting stock prices
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Price', color='tab:blue')
    ax1.plot(df.index, df['c'], label='Close', color='black')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.legend(loc='upper left')

    # Creating a twin axis for volume
    ax2 = ax1.twinx()  
    ax2.set_ylabel('Volume', color='tab:red')  
    ax2.bar(df.index, df['v'], color='tab:red', alpha=0.6)
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Title and layout
    plt.title('Stock Price and Volume')
    fig.tight_layout()  # To ensure a neat layout

    # Rotate x-axis labels directly on the axes object
    for label in ax1.get_xticklabels():
        label.set_rotation(45)

    # Show plot
    plt.show()

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

def convert_est_date_to_timestamp(date_string, date_format="%Y-%m-%d"):
    # Parse the date string into a datetime object
    date_obj = datetime.datetime.strptime(date_string, date_format)

    # Assign the Eastern Time zone to the datetime object
    eastern_time_zone = ZoneInfo('America/New_York')
    date_obj = date_obj.replace(tzinfo=eastern_time_zone)

    # Convert the datetime object to a UNIX timestamp
    timestamp = int(date_obj.timestamp())*1000

    return timestamp

def _run_1day_interval_example():
    # intraday 1 day
    start_date = convert_est_date_to_timestamp("2023-06-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
    end_date = convert_est_date_to_timestamp("2023-09-01T23:59:59", '%Y-%m-%dT%H:%M:%S')
    data_array = get_symbol_chart("AAPL", "1d", start_date, end_date)
    print_pretty(data_array)
    plot_chart_with_volume(data_array)


def _run_5min_interval_example():
    # intraday 5 min
    start_date = convert_est_date_to_timestamp("2023-06-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
    end_date = convert_est_date_to_timestamp("2023-06-01T23:59:59", '%Y-%m-%dT%H:%M:%S')
    data_array = get_symbol_chart("AAPL", "5min", start_date, end_date)
    print_pretty(data_array)
    plot_chart_with_volume(data_array)
    
def _run_5min_interval_excluding_pre_after_market_example():
    # intraday 5 min
    start_date = convert_est_date_to_timestamp("2023-06-01T00:00:00", '%Y-%m-%dT%H:%M:%S')
    end_date = convert_est_date_to_timestamp("2023-06-01T23:59:59", '%Y-%m-%dT%H:%M:%S')
    data_array = get_symbol_chart("AAPL", "5min", start_date, end_date)
    filtered_data_array = filter_out_pre_after_us_stock_market(data_array)
    print_pretty(filtered_data_array)
    plot_chart_with_volume(filtered_data_array)
  
if __name__ == "__main__":
    data_1 = _run_1day_interval_example()
    data_2 = _run_5min_interval_example()
    data_3 = _run_5min_interval_excluding_pre_after_market_example()
    