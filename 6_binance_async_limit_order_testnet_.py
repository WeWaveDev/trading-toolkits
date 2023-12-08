
import asyncio
import math

from binance import AsyncClient, BinanceSocketManager

from access import binance_test_net_api_key, binance_test_net_secret


async def place_order(client, symbol, quantity, price, order_type, order_status):
    if order_type == 'buy':
        order = await client.order_limit_buy(symbol=symbol, quantity=quantity, price=price)
    elif order_type == 'sell':
        order = await client.order_limit_sell(symbol=symbol, quantity=quantity, price=price)
    
    order_status[order['orderId']] = 'NEW'
    return order['orderId']

async def user_data_stream(client, symbol, order_status, event):
    bsm = BinanceSocketManager(client)
    async with bsm.user_socket() as user_socket:
        while True:
            msg = await user_socket.recv()
            if msg['e'] == 'executionReport' and msg['s'] == symbol:
                order_id = msg['i']
                order_status[order_id] = msg['X']
                if msg['X'] == 'FILLED':
                    event.set()

async def price_stream(client, symbol, buy_price, sell_price):
    bsm = BinanceSocketManager(client)
    async with bsm.symbol_ticker_socket(symbol) as ticker_socket:
        while True:
            res = await ticker_socket.recv()
            if res:
                # print the price and the delta to buy/sell price
                price = float(res['c'])
                print(f"\r{price} - ({round(price - buy_price, 5)}, {round(sell_price - price, 5)})", end="")

async def main():
    client = await AsyncClient.create(binance_test_net_api_key, binance_test_net_secret, testnet=True)
    order_status = {}
    symbol = 'BTCUSDT'
    quantity = 0.0005
    spread = 0.0001
    filled_event = asyncio.Event()

    price = float((await client.get_symbol_ticker(symbol=symbol))['price'])
    buy_price = math.floor(price * (1 - spread))
    sell_price = math.ceil(price * (1 + spread))

    asyncio.create_task(user_data_stream(client, symbol, order_status, filled_event))
    asyncio.create_task(price_stream(client, symbol, buy_price, sell_price))

    buy_order_id = await place_order(client, symbol, quantity, buy_price, 'buy', order_status)
    sell_order_id = await place_order(client, symbol, quantity, sell_price, 'sell', order_status)
    
    print('Waiting for order to fill... {}:{}, {}:{}'.format(buy_order_id, buy_price, sell_order_id, sell_price))

    await filled_event.wait()

    if order_status.get(buy_order_id) == 'FILLED':
        await client.cancel_order(symbol=symbol, orderId=sell_order_id)
    elif order_status.get(sell_order_id) == 'FILLED':
        await client.cancel_order(symbol=symbol, orderId=buy_order_id)

    order_id_filled = buy_order_id if order_status.get(buy_order_id) == 'FILLED' else sell_order_id
    # print the filled order
    order = await client.get_order(symbol=symbol, orderId=order_id_filled)
    print("\nFilled order:")
    print(order)
    
    print("\nOne order filled, remaining order cancelled.")

    await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
