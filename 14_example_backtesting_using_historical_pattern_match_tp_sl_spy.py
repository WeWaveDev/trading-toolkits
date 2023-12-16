import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG, SMA

from lib.data.chart import get_ohlc_history_in_dataframe
from lib.data.pattern_match import (
    call_historcial_pattern_match_by_milliseconds,
    summarize_matched_event_array,
)

'''
NOTE: in this example, we use the historical pattern match to generate the signal, and use the take profit and stop loss to exit the position

'''

symbol = 'SPY'
time_interval = '1D'
# Fetching the OHLC data
ohlc_history_in_dataframe = get_ohlc_history_in_dataframe(symbol, time_interval, '2022-01-01', '2023-01-01')

CALL_HISTORICAL_PATTERN_MATCH_EVERY_N_TRADING_DAYS = 5

date_to_object_dict = {}

def signal_generator(arr: pd.DatetimeIndex) -> pd.Series:
    signals = []

    for index, date in enumerate(arr):
        if index % CALL_HISTORICAL_PATTERN_MATCH_EVERY_N_TRADING_DAYS == 0: # project every N trading days
            # start_time_millisecond  = date -minus 60 days
            start_time_millisecond = date.timestamp() * 1000 - (1+60) * 24 * 60 * 60 * 1000 
            end_time_millisecond = date.timestamp() * 1000 - 1  * 24 * 60 * 60 * 1000 # end date -1 is because to simultae the real case that not letting the api know today's close price to avoid look ahead bias
            print('call WeWave historical pattern match', date, start_time_millisecond, end_time_millisecond)
            matched_event_array = call_historcial_pattern_match_by_milliseconds(
                symbol,
                start_time_millisecond,
                end_time_millisecond,
                time_interval
            )
            sumarized = summarize_matched_event_array(matched_event_array)
            print('sumarized', sumarized)
            if sumarized['mean_return'] > 0.3:
                signals.append(1)
                date_to_object_dict[date] ={
                    'direction': 1,
                    'take_profit_perc': sumarized['mean_return'] *2,
                    'stop_loss_perc': sumarized['mean_return'] * 2,
                    'limit_perc':  (-1*sumarized['min_return'] *0.1)  if sumarized['min_return'] <0 else None # make it positive
                }
                # if the limit_perc is larger than stop_loss_perc, then limit_perc will be 1/4 of stop_loss_perc
                # SL <  LIMIT < price < TP
                if date_to_object_dict[date]['limit_perc'] > date_to_object_dict[date]['stop_loss_perc']:
                    date_to_object_dict[date]['limit_perc'] = date_to_object_dict[date]['stop_loss_perc'] * 0.25
                
            elif sumarized['mean_return'] < -0.3:
                signals.append(-1)
                date_to_object_dict[date] = {
                        'direction': -1,
                        'take_profit_perc': -1*(sumarized['mean_return'])*2, # make it positive
                        'stop_loss_perc':  -1* sumarized['mean_return'] * 2, # make it positive
                        'limit_perc': sumarized['max_return'] *0.1 if sumarized['max_return'] >0 else None # make it positive
                    }
                # SL > LIMIT > price > TP
                if date_to_object_dict[date]['limit_perc'] > date_to_object_dict[date]['stop_loss_perc']:
                    date_to_object_dict[date]['limit_perc'] = date_to_object_dict[date]['stop_loss_perc'] * 0.25
                
                
            else:
                signals.append(0)
        else:    
            signals.append(0)

    # Convert the list of signals to a pandas Series and return
    return pd.Series(signals, index=arr)
    
    
class ProfitTargetStrategy(Strategy):
    def init(self):
        date = self.data.index
        self.signal = self.I(signal_generator, date)

    def next(self):
        current_price = self.data.Close[-1] 
        date_str_now = self.data.index[-1]
        # print current price, signal
        print('debug next', date_str_now, current_price, self.signal[-1])
        
        # print each order and its status
        # for order in self.orders:
        #     # attributes: is_long, is_short, limit, size, sl, tp, stop
        #     print('debug order', order.is_long, order.is_short, order.limit, order.size, order.sl, order.tp, order.stop)
            
        if date_str_now in date_to_object_dict:
            signal_object = date_to_object_dict[date_str_now]
        else:
            print('debug no signal_object')
            return # skip to prevent error
        
        if self.signal[-1] == 1:
        #     # clean unexecuted orders
        #     for order in self.orders:
        #         order.cancel()
                
            take_profit = (1+signal_object['take_profit_perc']*0.01) * current_price 
            stop_loss = (1-signal_object['stop_loss_perc']*0.01) * current_price 
            limit = (1-signal_object['limit_perc']*0.01) * current_price
            print('debug buy', current_price, take_profit, limit)
            self.buy(
                size=0.2, 
                # limit=limit,
                tp=take_profit, 
                sl=stop_loss
            ) 

        if self.signal[-1] == -1:
        #     # clean unexecuted orders
        #     for order in self.orders:
        #         order.cancel()
                
            take_profit = (1-signal_object['take_profit_perc']*0.01) * current_price 
            stop_loss = (1+signal_object['stop_loss_perc']*0.01) * current_price 
            limit = (1+signal_object['limit_perc']*0.01) * current_price
            print('debug sell', current_price, take_profit, limit, signal_object['take_profit_perc'])
            # SL > LIMIT > TP
            self.sell(
                size=0.2, 
                # limit=limit, 
                tp=take_profit, 
                sl=stop_loss
            ) 
                        
            
# Running the backtest
bt = Backtest(ohlc_history_in_dataframe, ProfitTargetStrategy, cash=10_000, commission=.002)
stats = bt.run()
bt.plot()
print(stats)
print('debug trades')
print(stats._trades)
