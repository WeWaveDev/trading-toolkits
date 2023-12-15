import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

from lib.data.chart import get_ohlc_history_in_dataframe
from lib.data.pattern_match import (
    call_historcial_pattern_match_by_milliseconds,
    summarize_matched_event_array,
)

symbol = 'SPY'
time_interval = '1D'
# Fetching the OHLC data
ohlc_history_in_dataframe = get_ohlc_history_in_dataframe(symbol, time_interval, '2022-01-01', '2023-01-01')


def signal_generator(arr: pd.DatetimeIndex) -> pd.Series:
    print('debug arr', arr  )
    # Create an empty list to store the signals
    signals = []

    # Iterate through each date in the series
    for index, date in enumerate(arr):

        if index % 10 == 0: # project every 10 trading days
            # start_time_millisecond  = date -minus 60 days
            start_time_millisecond = date.timestamp() * 1000 - 60 * 24 * 60 * 60 * 1000 
            end_time_millisecond = date.timestamp() * 1000
            print('call WeWave historical pattern match', date, start_time_millisecond, end_time_millisecond)
            matched_event_array = call_historcial_pattern_match_by_milliseconds(
                symbol,
                start_time_millisecond,
                end_time_millisecond,
                time_interval
            )
            sumarized = summarize_matched_event_array(matched_event_array)
            print('sumarized', sumarized)
            if sumarized['mean_return'] > 0.5:
                signals.append(1)
            elif sumarized['mean_return'] < -0.05:
                signals.append(-1)
            else:
                signals.append(0)
        else:    
            signals.append(0)


    # Convert the list of signals to a pandas Series and return
    return pd.Series(signals, index=arr)
    
    
class ProfitTargetStrategy(Strategy):
    sma_period = 20
    profit_ratio = 0.05  # 5% profit target
    profit_target_pct = 0.05
    counter = 0

    def init(self):
        close = self.data.Close
        date = self.data.index
        # Calculate the SMA
        self.sma = self.I(SMA, close, self.sma_period)
        self.signal = self.I(signal_generator, date)

    def next(self):
        print('debug next', self.signal[-1])
        if self.signal[-1] == 1:
            self.buy()
            
        if self.signal[-1] == 0:
            self.position.close()

        if self.signal[-1] == -1:
            self.sell()
            
# Running the backtest
bt = Backtest(ohlc_history_in_dataframe, ProfitTargetStrategy, cash=10_000, commission=.002)
stats = bt.run()
bt.plot()
print(stats)
