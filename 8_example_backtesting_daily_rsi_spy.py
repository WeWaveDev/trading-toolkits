import datetime

import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from lib.data.chart import get_ohlc_history_in_dataframe

now = datetime.datetime.now()
now_date_string = now.strftime('%Y-%m-%d')

ohlc_history_in_dataframe = get_ohlc_history_in_dataframe('SPY', '1D', '2013-01-01', now_date_string )


class RsiOscillator(Strategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    # Do as much initial computation as possible
    def init(self):
        self.rsi = self.I(ta.rsi, pd.Series(self.data.Close), self.rsi_window)

    # Step through bars one by one
    # Note that multiple buys are a thing here
    def next(self):
        if crossover(self.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.rsi):
            self.buy()

bt = Backtest(ohlc_history_in_dataframe, RsiOscillator, cash=10_000, commission=.002)
stats = bt.run()
bt.plot()
print(stats)
