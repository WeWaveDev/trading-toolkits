import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

from lib.data.chart import get_ohlc_history_in_dataframe

# Fetching the OHLC data
ohlc_history_in_dataframe = get_ohlc_history_in_dataframe('SPY', '1D', '2018-01-01', '2023-01-01')


def signal_generator(arr: pd.DatetimeIndex) -> pd.Series:
    print('debug arr', arr  )
    # Create an empty list to store the signals
    signals = []

    # Iterate through each date in the series
    for date in arr:
        # Check the day of the week and assign the signal
        if date.weekday() == 3:  # Thursday
            signals.append(1)
        elif date.weekday() == 1:  # Tuesday
            signals.append(-1)
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
        # If the signal is 1 (Monday), and the current price is above the SMA, buy
        if self.signal[-1] == 1:
            self.buy()

        # If the signal is -1 (Friday), close the position if any
        if self.signal[-1] == -1:
            self.position.close()
            
# Running the backtest
bt = Backtest(ohlc_history_in_dataframe, ProfitTargetStrategy, cash=10_000, commission=.002)
stats = bt.run()
bt.plot()
print(stats)
