import os
import openai
import pprint
from binance.um_futures import UMFutures
from binance.um_futures.market import exchange_info
from binance.um_futures.market import ticker_price
import pandas as pd
from datetime import datetime, timezone
import pandas_ta as pta
import time
from binance.lib.utils import get_timestamp 

# ==================== default setting ========================
global len_limit
global usdt

# wish_list =['TUSDT', 'STXUSDT', 'SXPUSDT', 'MASKUSDT', 'APTUSDT']
# 사고싶은 종목 
wish_list =['APTUSDT']

# 돌릴 종목 갯수
len_limit = 1


# ==============================================================

def refresh_asset():
    global usdt
    global avail_asset
    assets = um_futures_client.account()['assets']

    for i in assets:
        if i['asset'] == 'USDT':
            usdt = float(i['availableBalance'])
        if float(i['walletBalance']) != 0 and i['asset'] != 'USDT':
            avail_asset[i['asset']] = i['walletBalance']

def order_bid(list):
    global usdt
    print(usdt)
    if len(list) == 0:
        return usdt / 2
    else :
        return usdt
    
def buy_quantity(list, symbols) :
    global usdt
    global len_limit

    price = float(um_futures_client.ticker_price(symbol = symbols)["price"])

    print("price = ", price)

    buy_usdt = usdt*((1/(len_limit-len(list)))/1.0004)

    print("balance = ", round(buy_usdt / 2 / price, 1))
    
    return round(buy_usdt / 2 / price, 1)

    # if len(list) == 0:
    #     usdt*((1/(len_limit-len(list)))/1.0004)
    #     print(symbols, round(usdt / 2 / price, 1))
    #     return round(usdt / 2 / price, 1)
    # else :
    #     return round(usdt / price, 1)

def sell_quantity(list, symbols):
    print()

def my_balance():
    global usdt
    # Get account information
    assets = um_futures_client.account()['assets']
    for i in assets:
        if i['asset'] == 'USDT':
            usdt = float(i['walletBalance'])



um_futures_client = UMFutures(key='Your Access key',
                               secret='Your Secret key')

# um_futures_client.change_position_mode(dualSidePosition="true", timestamp = get_timestamp())

# Get account information
assets = um_futures_client.account()['assets']

print(um_futures_client.get_position_risk(symbol="APTUSDT", timestamp=get_timestamp()))

# print(um_futures_client.get_all_orders(symbol="APTUSDT", timestamp=get_timestamp()))


buy_list = []
wish_symbol_list = []
symbol_list = []
avail_asset = {}


for i in assets:
    if i['asset'] == 'USDT':
        usdt = float(i['availableBalance'])
    if float(i['walletBalance']) != 0 and i['asset'] != 'USDT':
        avail_asset[i['asset']] = i['walletBalance']

# Get exchange information
ex_list = um_futures_client.exchange_info()
ex_list_symbols = ex_list['symbols']

#print(assets)
print(usdt)
print("avail asset" , avail_asset)


for i in ex_list_symbols:
    symbol_list.append(i['symbol'])


for i in ex_list_symbols:
    if i['symbol'] in wish_list:
        wish_symbol_list.append(i)

rsi_list = {}

## 첫 start에서 long position buy

# um_futures_client.new_order(symbol='APTUSDT', positionSide="LONG", side="BUY", type="MARKET", timestamp = get_timestamp() ,quantity = buy_quantity(buy_list,'APTUSDT'))
# buy_list.append('APTUSDT')

assets = um_futures_client.account()['assets']

print(get_timestamp())

for i in assets:
    if i['asset'] == 'USDT':
        usdt = float(i['availableBalance'])
    if float(i['walletBalance']) != 0 and i['asset'] != 'USDT':
        avail_asset[i['asset']] = i['walletBalance']

while True:

    for i in wish_symbol_list:
        klines = um_futures_client.klines(i['symbol'], '15m', limit=200)
        df = pd.DataFrame(data= {
            'open_time': [datetime.fromtimestamp(x[0] / 1000, timezone.utc) for x in klines],
            'open': [float(x[1]) for x in klines],
            'close': [float(x[4]) for x in klines],
        })
        ta_rsi = pta.rsi(df['close'], length=14)
        rsi_list[i['symbol']] = ta_rsi
    
    for i in rsi_list:
        print(" ============== ", i, "rsi ================")
        print(i)
        print(rsi_list[i])
        print(" ==========================================")
        if rsi_list[i][199] >= 80:
            # long position sell
            um_futures_client.new_order(symbol=i, positionSide="LONG", side="SELL", type="MARKET", timestamp = get_timestamp() ,quantity = avail_asset[i])
            buy_list.remove(i)

            assets = um_futures_client.account()['assets']

            for j in assets:
                if j['asset'] == 'USDT':
                    usdt = float(j['availableBalance'])
                if float(j['walletBalance']) != 0 and j['asset'] != 'USDT':
                    avail_asset[j['asset']] = j['walletBalance']


            # short position buy
            um_futures_client.new_order(symbol=i, positionSide="SHORT", side="BUY", type="MARKET", timestamp = get_timestamp() ,quantity = buy_quantity(buy_list,i))
            buy_list.append(i)

            assets = um_futures_client.account()['assets']

            for j in assets:
                if j['asset'] == 'USDT':
                    usdt = float(j['availableBalance'])
                if float(j['walletBalance']) != 0 and j['asset'] != 'USDT':
                    avail_asset[j['asset']] = j['walletBalance']


    for i in buy_list:
        if rsi_list[i][199] <= 20:
            
            # SHORT position sell
            um_futures_client.new_order(symbol=i, positionSide="SHORT", side="SELL", type="MARKET", timestamp = get_timestamp() ,quantity = avail_asset[i])
            buy_list.remove(i)

            assets = um_futures_client.account()['assets']

            for j in assets:
                if j['asset'] == 'USDT':
                    usdt = float(j['availableBalance'])
                if float(j['walletBalance']) != 0 and j['asset'] != 'USDT':
                    avail_asset[j['asset']] = j['walletBalance']


            # short position buy
            um_futures_client.new_order(symbol=i, positionSide="LONG", side="BUY", type="MARKET", timestamp = get_timestamp() ,quantity = buy_quantity(buy_list,i))
            buy_list.append(i)

            assets = um_futures_client.account()['assets']

            for j in assets:
                if j['asset'] == 'USDT':
                    usdt = float(j['availableBalance'])
                if float(j['walletBalance']) != 0 and j['asset'] != 'USDT':
                    avail_asset[j['asset']] = j['walletBalance']

    print("buy list ", avail_asset)
    print("current usdt balance: ", usdt)
    my_balance()
    time.sleep(5)