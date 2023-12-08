import asyncio
import math

from binance import AsyncClient, BinanceSocketManager

from access import binance_test_net_api_key, binance_test_net_secret


async def main():
    # Your existing order logic
    symbol = 'BTCUSDT'
    quantity = 0.0006
    spread = 0.0002

    client = await AsyncClient.create(binance_test_net_api_key, binance_test_net_secret, tld='us', testnet=True)
    price = float((await client.get_symbol_ticker(symbol=symbol))['price'])
    limit_buy_order_price = math.floor(price * (1 - spread))

    order = await client.order_limit_buy(
        symbol=symbol,
        quantity=quantity,
        price=limit_buy_order_price)

    sell_price = math.ceil(price * (1 + spread))
    await client.order_limit_sell(
        symbol=symbol,
        quantity=quantity,
        price=sell_price)

    async with BinanceSocketManager(client) as bsm:
        user_socket = bsm.user_socket()

        async for msg in user_socket:
            if msg['e'] == 'executionReport' and msg['x'] == 'FILLED':
                print("\nOrder filled, cleaning up remaining orders...")
                # Cancel all open orders
                orders = await client.get_open_orders(symbol=symbol)
                for order in orders:
                    await client.cancel_order(symbol=symbol, orderId=order['orderId'])
                    print(f"Cancelled order {order['orderId']}")

async def timer():
    start_time = asyncio.get_running_loop().time()
    while True:
        elapsed_time = asyncio.get_running_loop().time() - start_time
        print(f"\rSeconds elapsed: {int(elapsed_time)}", end="")
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(main(), timer()))
