import datetime

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

from lib.data.chart import get_ohlc_history_in_dataframe

'''
 Backtest a strategy with update to date daily data of $SPY.
 - Buy when price cross above 100 day moving average.
 - Sell when price cross below 100 day moving average.
'''
now = datetime.datetime.now()
now_date_string = now.strftime('%Y-%m-%d')

ohlc_history_in_dataframe = get_ohlc_history_in_dataframe('SPY', '1D', '2013-01-01', now_date_string )

print(ohlc_history_in_dataframe.head())
print(ohlc_history_in_dataframe.tail())

class SmaCross(Strategy):
    n1 = 1
    n2 = 100

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


bt = Backtest(ohlc_history_in_dataframe, SmaCross,
              cash=10000, commission=.002,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()
