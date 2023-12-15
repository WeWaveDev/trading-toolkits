import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

from lib.data.chart import get_ohlc_history_in_dataframe

# Fetching the OHLC data
ohlc_history_in_dataframe = get_ohlc_history_in_dataframe('SPY', '1D', '2013-01-01', '2023-01-01')


def signal_generator(arr: pd.DatetimeIndex) -> pd.Series:
    # 'Buy In October And Sell In May' Strategy
    print('debug arr', arr  )
    signals = []
    # return -1 when it is in May
    # return 1 when it is in October
    for date in arr:
        if date.month == 10:  # Buy in October
            signals.append(1)
        elif date.month == 5:  # Sell in May
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
    each_size = 0.05

    def init(self):
        close = self.data.Close
        date = self.data.index
        # Calculate the SMA
        self.sma = self.I(SMA, close, self.sma_period)
        self.signal = self.I(signal_generator, date)

    def next(self):
        if self.signal[-1] == 1:
            self.buy(size=self.each_size)

        if self.signal[-1] == -1:
            self.position.close()
            
# Running the backtest
bt = Backtest(ohlc_history_in_dataframe, ProfitTargetStrategy, cash=10_000, commission=.002)
stats = bt.run()
bt.plot()
print(stats)
