import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

from lib.data.chart import get_symbol_chart
from lib.data.pattern_match import call_historcial_pattern_match_by_milliseconds
from lib.data.time_randomizer import get_randomized_start_and_end_date_dict
from lib.data.time_utils import get_extended_end_time_based_on_milliseconds


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
    


def create_distribution_plots(storage_for_plotting_historical_projection, storage_for_history_market):
    # for each close price from times[matched_event_datapoints:] - times[matched_event_datapoints-1]
    
    list_of_days_since_matched_event = [] # assume we enter the position on matched_event_datapoints-1
    list_of_return_percentage = []
    for data in storage_for_plotting_historical_projection:
        matched_event_candles = data['matched_event_candles']
        matched_event_datapoints = data['matched_event_datapoints']
        closing_values = [candle['c'] for candle in matched_event_candles]
        return_precentage = 100*(closing_values[-1] - closing_values[matched_event_datapoints-1]) / closing_values[matched_event_datapoints-1] if closing_values[matched_event_datapoints-1] > 0 else 0
        list_of_return_percentage.append(return_precentage)
        days = len(closing_values) - matched_event_datapoints
        list_of_days_since_matched_event.append(days)

    # fit a normal distribution
    mu, std = norm.fit(list_of_return_percentage)
    print('debug mu, std', mu, std)
    
    # Calculate quartiles, median, min, and max
    p25 = np.percentile(list_of_return_percentage, 25)
    median = np.percentile(list_of_return_percentage, 50)
    p75 = np.percentile(list_of_return_percentage, 75)
    minv = np.min(list_of_return_percentage)
    maxv = np.max(list_of_return_percentage)    
    
    # for the market outcome
    market_outcome_instance = storage_for_history_market[0]
    matched_event_candles = market_outcome_instance['matched_event_candles']
    matched_event_datapoints = market_outcome_instance['matched_event_datapoints']
    closing_values = [candle['c'] for candle in matched_event_candles]
    market_outcome_return_percentage = 100*(closing_values[-1] - closing_values[matched_event_datapoints-1]) / closing_values[matched_event_datapoints-1] if closing_values[matched_event_datapoints-1] > 0 else 0
    days = len(closing_values) - matched_event_datapoints
    list_of_days_since_matched_event.append(days)
    
    print('debug list_of_days_since_matched_event', list_of_days_since_matched_event)
        
    # plot 
    fig, axs = plt.subplots(1, 1, figsize=(12, 4), constrained_layout=True)
    axs.hist(list_of_return_percentage, bins=60)
    
    # Plot normal distribution curve
    ax2 = axs.twinx()
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    ax2.plot(x, p, 'grey', linewidth=1, label='Normal Distribution')
    ax2.set_ylabel('Probability Density', color='grey')
    distribution_title = "Fit results: mu = {:.2f},  std = {:.2f}".format(mu, std)
    
    # Optional: Add a line for a specific percentile
    plt.axvline(x=mu, color='red', ls='--')
    plt.axvline(x=mu+std, color='orange', ls='-')
    plt.axvline(x=mu-std, color='salmon', ls='-')
    plt.axvline(x=p25, color='purple', ls=':')
    plt.axvline(x=median, color='black', ls=':')
    plt.axvline(x=p75, color='lime', ls=':')
    plt.axvline(x=minv, color='blue', ls='-.')
    plt.axvline(x=maxv, color='navy', ls='-.')


    axs.axvline(x=market_outcome_return_percentage, color='red', label='Market Outcome')
    
    axs.set_title('Distribution of Projection in {} days\n {}'.format(list_of_days_since_matched_event[0], distribution_title))
    
    # axs.legend()
    plt.legend([
        "Normal Distribution",
        "Mean", 
        "+Standard Deviation",
        "-Standard Deviation", 
        "25th Percentile",
        "50th Percentile or Median", 
        "75th Percentile",
        "Minimum Value", 
        "Maximum Value"]
    )
    # plt.show()
    plt.savefig(os.path.join('local_results', '4_2.png'))
    print('resuts saved to local_results/')
    

def create_subplots(storage_for_plotting_historical_projection, storage_for_history_market):
    # Determine the number of rows and columns for subplots
    data_array = storage_for_plotting_historical_projection + storage_for_history_market
    num_subcharts = len(data_array)
    if num_subcharts == 0:
        print('no data to plot')
        return
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
            # add subtitle if any
            if 'subtitle' in subchart_data:
                ax.set_title(f'Subchart {i+1}: {subchart_data["matched_start_date_string"]} to {subchart_data["matched_end_date_string"]}\n{subchart_data["subtitle"]}', fontsize=5)
            else:
                ax.set_title(f'Subchart {i+1}: {subchart_data["matched_start_date_string"]} to {subchart_data["matched_end_date_string"]}', fontsize=5)

            ax.set_xticks([times[0], times[matched_event_datapoints], times[-1]])
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
        else:
            # Hide unused subplots
            ax.axis('off')

    plt.suptitle('Matched Event Candles: Matched Zone vs Prediction Zone in Subcharts')
    plt.savefig(os.path.join('local_results', '4_1.png'))


if __name__ == '__main__':
    # NOTE: this example is daily
    date_dict = get_randomized_start_and_end_date_dict(
        start_time_string='1980-01-01',
        end_time_string='2023-11-01',
        random_days_min=20,
        random_days_max=60,
    )
    start_time_millisecond = date_dict['start_time_millisecond']
    end_time_millisecond = date_dict['end_time_millisecond']    
    
    symbol = 'INDX:SPX'
    time_interval = '1d'
    
    matched_event_array = call_historcial_pattern_match_by_milliseconds(
        symbol,
        start_time_millisecond,
        end_time_millisecond,
        time_interval
    )
    
    extended_end_time = get_extended_end_time_based_on_milliseconds(
        start_time_millisecond,
        end_time_millisecond,
    )
    real_history = get_symbol_chart(symbol, time_interval, start_time_millisecond, extended_end_time)


    matched_event_array_top = matched_event_array[:] # NOTE: consider the first 20 results or all
    
    storage_for_plotting_historical_projection = []

    for index, matched_event in enumerate(matched_event_array_top):
        print('matched event #{}'.format(index))
        matched_start_date = matched_event['startDate']
        matched_end_date = matched_event['endDate']
        matched_score = matched_event['score']
        # xToYScale = matched_event['xToYScale']
        # xToYOffset = matched_event['xToYOffset']
        matched_event_candles = matched_event['candles']        
        matched_event_datapoints = matched_event['dataPoints']    
                
        matched_start_date_string = datetime.datetime.fromtimestamp(matched_start_date / 1000.0)
        matched_end_date_string = datetime.datetime.fromtimestamp(matched_end_date / 1000.0)
        
        print('matched start date: {}, {} UTC'.format(matched_start_date, matched_start_date_string))
        print('matched end date: {} {} UTC'.format(matched_end_date, matched_end_date_string))
        print('matched score: {}'.format(matched_score))

        # print projections
        print('matched_event_datapoints', matched_event_datapoints, len(matched_event_candles))
        print('matched zone index {} to {}'. format(0, matched_event_datapoints-1))
        print('prediction zone index {} to {}'. format(matched_event_datapoints, len(matched_event_candles)-1))
        
        storage_for_plotting_historical_projection.append(
            {
                'matched_event_candles': matched_event_candles,
                'matched_event_datapoints': matched_event_datapoints,
                'matched_start_date_string': matched_start_date_string,
                'matched_end_date_string': matched_end_date_string,
            }
        )    
        print('---------------------------------')
        
        # plot_pattern_match_and_prediction(matched_event_candles, matched_event_datapoints)
        
    storage_for_history_market = []
    if len(matched_event_array_top) > 0:
        # added the hisotrca data to storage_for_plotting
        storage_for_history_market.append(
            {
                'matched_event_candles': real_history,
                'matched_event_datapoints': matched_event_array_top[0]['dataPoints'] ,
                'matched_start_date_string': datetime.datetime.fromtimestamp(start_time_millisecond / 1000.0),
                'matched_end_date_string': datetime.datetime.fromtimestamp(extended_end_time / 1000.0),
                'subtitle': 'The history of market ends up with'
            }
        )
        
    create_subplots(storage_for_plotting_historical_projection, storage_for_history_market)
    create_distribution_plots(storage_for_plotting_historical_projection, storage_for_history_market)
        
            
            
    
    
