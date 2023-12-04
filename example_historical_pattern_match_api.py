import datetime
import os

import matplotlib.pyplot as plt
import numpy as np

from lib.data.pattern_match import call_historcial_pattern_match


def plot_pattern_match_and_prediction(matched_event_candles, matched_event_datapoints):
    # Extracting time and closing values
    times = [candle['t'] for candle in matched_event_candles]
    closing_values = [candle['c'] for candle in matched_event_candles]

    # Plotting the lines with different colors
    plt.figure(figsize=(10, 5))
    plt.plot(times[:matched_event_datapoints], closing_values[:matched_event_datapoints], color='blue', label='Matched Zone')
    plt.plot(times[matched_event_datapoints:], closing_values[matched_event_datapoints:], color='red', label='Prediction Zone')
    plt.xlabel('Time')
    plt.ylabel('Closing Value')
    plt.title('Matched Zone vs Prediction Zone')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
def plot_all_matches(data_array):
    # Adjusting the script to handle 20 subcharts of matched_event_candles

    # Generating sample data for 20 subcharts
    subcharts_data = []
    for i in range(20):
        subchart = [{'t': f'2023-01-{i+1:02d}', 'c': 50 + i*2 + j} for j in range(8)]
        subcharts_data.append(subchart)

    # Defining matched_event_datapoints for each subchart
    matched_event_datapoints = 5

    # Plotting 20 subcharts
    fig, axs = plt.subplots(5, 4, figsize=(20, 15), constrained_layout=True)

    for i, ax in enumerate(axs.flatten()):
        if i < len(subcharts_data):
            times = [candle['t'] for candle in subcharts_data[i]]
            closing_values = [candle['c'] for candle in subcharts_data[i]]

            ax.plot(times[:matched_event_datapoints], closing_values[:matched_event_datapoints], color='blue')
            ax.plot(times[matched_event_datapoints:], closing_values[matched_event_datapoints:], color='red')
            ax.set_title(f'Subchart {i+1}')
            ax.tick_params(axis='x', rotation=45)

    plt.suptitle('Matched Event Candles: Matched Zone vs Prediction Zone in Subcharts')
    plt.show()

def create_subplots(data_array):
    # Determine the number of rows and columns for subplots
    num_subcharts = len(data_array)
    rows = int(np.ceil(num_subcharts / 4))
    cols = min(num_subcharts, 4)

    fig, axs = plt.subplots(rows, cols, figsize=(12, 2 * rows), constrained_layout=True)

    # Flatten the axes array for easy indexing
    axs = axs.flatten()

    for i, ax in enumerate(axs):
        if i < num_subcharts:
            subchart_data = data_array[i]
            matched_event_candles = subchart_data['matched_event_candles']
            matched_event_datapoints = subchart_data['matched_event_datapoints']
            
            # convert candle['t'] to utc datetime
            times = [datetime.datetime.utcfromtimestamp(candle['t'] / 1000.0).strftime('%Y-%m-%d') for candle in matched_event_candles]
            closing_values = [candle['c'] for candle in matched_event_candles]

            ax.plot(times[:matched_event_datapoints], closing_values[:matched_event_datapoints], color='blue')
            ax.plot(times[matched_event_datapoints:], closing_values[matched_event_datapoints:], color='red')
            ax.set_title(f'Subchart {i+1}: {subchart_data["matched_start_date_string"]} to {subchart_data["matched_end_date_string"]}', fontsize=5)
            
            ax.set_xticks([times[0], times[matched_event_datapoints], times[-1]])
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
        else:
            # Hide unused subplots
            ax.axis('off')

    plt.suptitle('Matched Event Candles: Matched Zone vs Prediction Zone in Subcharts')
    plt.show()


if __name__ == '__main__':
    start_time_to_match_pattern = '2023-04-01'
    end_time_to_match_pattern = '2023-07-01'
    symbol = 'SPY'
    
    matched_event_array = call_historcial_pattern_match(
        symbol,
        start_time_to_match_pattern,
        end_time_to_match_pattern
    )
    
    # for key, value in json_response['data']:
    #     print(key)

    matched_event_array_top = matched_event_array[:20] # NOTE: consider the first 20 results
    
    storage_for_plotting = []

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
        
        # print('\nmatched zone original data')
        # for index, candle in enumerate(matched_event_candles[:matched_event_datapoints]):
        #     print(index, candle.get('t'), candle.get('c'))
        
        # print('\nprediction zone original data')
        # for index, candle in enumerate(matched_event_candles[matched_event_datapoints:]):
        #     print(index, candle.get('c'))
        
        storage_for_plotting.append(
            {
                'matched_event_candles': matched_event_candles,
                'matched_event_datapoints': matched_event_datapoints,
                'matched_start_date_string': matched_start_date_string,
                'matched_end_date_string': matched_end_date_string,
            }
        )    
        print('---------------------------------')
        
        # plot_pattern_match_and_prediction(matched_event_candles, matched_event_datapoints)
    create_subplots(storage_for_plotting)
        
            
            
    
    
