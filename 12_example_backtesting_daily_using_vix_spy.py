import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.test import SMA

from lib.data.chart import get_ohlc_history_in_dataframe

start_date = '2003-01-01'
end_date = '2023-01-01'

spy_data = get_ohlc_history_in_dataframe('SPY', '1D', start_date, end_date)
vix_data = get_ohlc_history_in_dataframe('INDX:VIX', '1D', start_date, end_date)

def only_keep_the_same_dates(df1: pd.DataFrame, df2: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    df1_dates = df1.index
    df2_dates = df2.index
    same_dates = df1_dates.intersection(df2_dates)
    return df1.loc[same_dates], df2.loc[same_dates]

# print the length of the dataframes
print('spy_data', len(spy_data))
print('vix_data', len(vix_data))
spy_data, vix_data = only_keep_the_same_dates(spy_data, vix_data)

# print the length of the dataframes
print('spy_data', len(spy_data))
print('vix_data', len(vix_data))


class VIXBasedSPYStrategy(Strategy):
    vix_threshold_high = 30  # Example threshold for high VIX
    vix_threshold_low = 20   # Example threshold for low VIX

    def init(self):
        # Assuming self.data1 is VIX data and self.data is SPY data
        self.vix_open = self.I(SMA, vix_data.Open, 1)

    def next(self):
        # If VIX is high, consider buying SPY
        if self.vix_open[-1] > self.vix_threshold_high:
            if not self.position:
                self.buy()

        # If VIX is low, consider selling SPY
        elif self.vix_open[-1] < self.vix_threshold_low:
            if self.position:
                self.position.close()

bt = Backtest(spy_data, VIXBasedSPYStrategy, cash=10_000, commission=.002)
stats = bt.run()
print(stats)
bt.plot()
