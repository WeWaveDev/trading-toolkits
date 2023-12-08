import math
import threading
import time

from binance import Client, ThreadedDepthCacheManager, ThreadedWebsocketManager
from binance.client import Client

from access import binance_test_net_api_key, binance_test_net_secret

# from binance.streams import BinanceSocketManager


# use CCXT to fetch all the symbols?

# NOTE: register your account at https://testnet.binance.vision/
client = Client(binance_test_net_api_key, binance_test_net_secret, tld='us', testnet=True)
# get all symbol prices
prices = client.get_all_tickers()

# only print the symbol inculding BTC
for price in prices:
    if 'BTC' in price['symbol'] and 'USD' in price['symbol']:
        print(price['symbol'], ': ', price['price'])


# # place a test market buy order, to place an actual order use the create_order function
# order = client.create_test_order(
#     symbol='BTCUSDT',
#     side=Client.SIDE_BUY,
#     type=Client.ORDER_TYPE_MARKET,
#     quantity=0.01)

# print(order)


symbol_info = client.get_symbol_info('BTCUSDT')
# print it prettily
import json

print(json.dumps(symbol_info, indent=4))


market_depth = client.get_order_book(symbol='BTCUSDT')
# print(json.dumps(market_depth, indent=4))


import pandas as pd

bids = pd.DataFrame(market_depth['bids'])
bids.columns = ['price', 'bids']
asks = pd.DataFrame(market_depth['asks'])
asks.columns = ['price', 'asks']
df = pd.concat([bids, asks]).fillna(0)
print(df)


recent_trades = client.get_recent_trades(symbol='BTCUSDT')
df = pd.DataFrame(recent_trades)
print("\nRecent trades:")
print(df)

def print_my_last_n_trades(symbol, n):
    trades = client.get_my_trades(symbol=symbol)
    df = pd.DataFrame(trades)
    print(f"\nLast {n} trades:")
    # in print show all columns
    pd.set_option('display.max_columns', None)
    print(df.tail(n))
        
    


info = client.get_account()
print("\nAccount info:")
print(json.dumps(symbol_info, indent=1))

trades = client.get_my_trades(symbol='BTCUSDT')
print("\nTrades:")
print(json.dumps(trades, indent=1))

def print_my_balance():
    asset_blance = client.get_asset_balance(asset='BTC')
    print("\nAsset balance:")
    print(json.dumps(asset_blance, indent=1))

    asset_blance = client.get_asset_balance(asset='USDT')
    print("\nAsset balance:")
    print(json.dumps(asset_blance, indent=1))
    

def print_my_open_orders(symbol):
    orders = client.get_open_orders(symbol='BTCUSDT')
    print("\nOpen orders:")
    print(json.dumps(orders, indent=1))


print_my_open_orders(symbol='BTCUSDT')
print_my_balance()

# NOTE: this is just testing
buy_test_order = client.create_test_order(
    symbol='BTCUSDT',
    side=Client.SIDE_BUY,
    type=Client.ORDER_TYPE_MARKET,
    quantity=0.0005
)

try:
    order = client.order_market_buy(
        symbol='BTCUSDT',
        quantity=0.0005)
    print("\nMarket buy order submitted:")
except Exception as e:
    print(e)
    
    
import math

try: 
    symbol = 'BTCUSDT'
    quantity = 0.0007
    spread = 0.00001
    price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    limit_buy_price = math.floor(price * (1 - spread))
    order = client.order_limit_buy(
        symbol=symbol,
        quantity=quantity,
        price=limit_buy_price)
    
    # sell when price is 5% higher than the buy price
    limit_sell_price = math.ceil(price * (1 + spread))
    order = client.order_limit_sell(
        symbol=symbol,
        quantity=quantity,
        price=limit_sell_price)
except Exception as e:
    print(e)
    
    
# trades = client.get_my_trades(symbol='BTCUSDT')
# print("\nTrades:")
# print(json.dumps(trades, indent=1))


# print_my_balance()
# print_my_open_orders(symbol='BTCUSDT')


# wait for 10 seconds & print count down
import time

for i in range(10, 0, -1):
    print(i)
    time.sleep(1)
    


# symbol = 'BTCUSDT'
# def process_message(msg):
#     if msg['e'] == 'executionReport' and msg['x'] == 'FILLED':
#         print("Order filled, cleaning up remaining orders...")
#         # print the filled order
#         print(json.dumps(msg, indent=4))
#         # Cancel all open orders
#         orders = client.get_open_orders(symbol=symbol)
#         for order in orders:
#             result = client.cancel_order(symbol=symbol, orderId=order['orderId'])
#             print(result)
#         print_my_open_orders(symbol='BTCUSDT')
#         print_my_balance()

# bm = BinanceSocketManager(client)
# conn_key = bm.start_user_socket(process_message)
# bm.start()


# def seconds_counter():
#     start_time = time.time()
#     while True:
#         elapsed_time = time.time() - start_time
#         print(f"\rSeconds elapsed: {int(elapsed_time)}", end="")
#         time.sleep(1)

# # Start the seconds counter thread
# counter_thread = threading.Thread(target=seconds_counter)
# counter_thread.start()


# cancel all orders
orders = client.get_open_orders(symbol='BTCUSDT')
for order in orders:
    try:
        result = client.cancel_order(
            symbol='BTCUSDT',
            orderId=order['orderId'])
        print(result)
    except Exception as e:
        print(e)

            
print_my_open_orders(symbol='BTCUSDT')
print_my_last_n_trades(symbol='BTCUSDT', n=6)
print_my_balance()