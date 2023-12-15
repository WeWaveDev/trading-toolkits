import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

from lib.data.chart import get_ohlc_history_in_dataframe

# Fetching the OHLC data
ohlc_history_in_dataframe = get_ohlc_history_in_dataframe('SPY', '1D', '2013-01-01', '2023-01-01')

class ProfitTargetStrategy(Strategy):
    sma_period = 20
    profit_ratio = 0.05  # 5% profit target
    profit_target_pct = 0.05

    def init(self):
        close = self.data.Close
        # Calculate the SMA
        self.sma = self.I(SMA, close, self.sma_period)

    def next(self):
        # If no position is open and the current price is above the SMA, buy
        if not self.position and self.data.Close[-1] > self.sma[-1]:
            self.buy()

        # Check if the current position has reached the profit target
        if self.position and self.position.pl_pct >= self.profit_target_pct:
            # print all positions
            print(self.position)
            self.position.close()
            
# Running the backtest
bt = Backtest(ohlc_history_in_dataframe, ProfitTargetStrategy, cash=10_000, commission=.002)
stats = bt.run()
bt.plot()
print(stats)
