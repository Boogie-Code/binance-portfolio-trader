from logging import error
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import config, csv, mysql.connector, sys
from datetime import datetime, timedelta

# current_time = datetime.now()
# print(current_time)

#   Define variables for the database 'binance_account'
host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

#   Connect to Binance
client = Client(config.API_KEY, config.API_SECRET)

#   Connect to MySQL database 'binance_account'
mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')
mycursor = mydb.cursor()

# Define a python list of coins from the csv to iterate over
spot_coins_traded = []
sql = '''SELECT * FROM spotSymbolsTraded'''
mycursor.execute(sql)
for items in mycursor.fetchall():
    spot_coins_traded.append(items[1])

try:
    for x in spot_coins_traded:
        try:
            spot_balances = client.get_asset_balance(asset=x)
            ticker = str(x)+'BUSD'            
            current_time = datetime.utcnow()
            current_time_minus_1min = current_time - timedelta(minutes=2)
            usdprice = client.get_historical_klines(symbol=ticker,interval=KLINE_INTERVAL_1MINUTE,start_str=str(current_time_minus_1min),end_str=str(current_time))
            current_time = datetime.now()
            list = [ticker[:-4],
                    spot_balances['free'],
                    current_time,
                    usdprice[0][1],
                    float(spot_balances['free'])*float(usdprice[0][1])]
            sql = """ INSERT INTO spotBalances (symbol, spotQty, updateTime, lastPrice, totalUSDValue) VALUES (%s, %s, %s, %s, %s) """
            val = list
            if float(spot_balances['free']) > 0:
                mycursor.execute(sql,val)
        except BinanceAPIException:
            try:
                spot_balances = client.get_asset_balance(asset=x)
                ticker = str(x)+'BTC'
                current_time = datetime.utcnow()       
                current_time_minus_1min = current_time - timedelta(minutes=2)
                usdprice = client.get_historical_klines(symbol=ticker,interval=KLINE_INTERVAL_1MINUTE,start_str=str(current_time_minus_1min),end_str=str(current_time))
                avgprice = client.get_avg_price(symbol='BTCBUSD')
                current_time = datetime.now()
                list = [ticker[:-3],
                        spot_balances['free'],
                        current_time,
                        usdprice[0][1],
                        float(spot_balances['free'])*float(usdprice[0][1])*float(avgprice['price'])]
                sql = """ INSERT INTO spotBalances (symbol, spotQty, updateTime, lastPrice, totalUSDValue) VALUES (%s, %s, %s, %s, %s) """
                val = list
                if float(spot_balances['free']) > 0:
                     mycursor.execute(sql,val)
            except BinanceAPIException:
                print('\t',ticker, 'Raised an Exception Error')
                pass
except error:
    pass

print('\tFinished checking spot coin balances')

#Get BUSD and USDT balances
stablecoins = ['USDT','BUSD']
for item in stablecoins:
    spot_balances = client.get_asset_balance(asset=item)
    current_time = datetime.now()
    list = [item,
        spot_balances['free'],
        current_time,
        1.0,
        spot_balances['free']]
    sql = """ INSERT INTO spotBalances (symbol, spotQty, updateTime, lastPrice, totalUSDValue) VALUES (%s, %s, %s, %s, %s) """
    val = list
    if float(spot_balances['free']) > 0:
        mycursor.execute(sql,val)

mydb.commit()

current_time = datetime.now()
print('\tFinished checking stablecoins')
print('FINISHED CHECKING SPOT BALANCES AT:\t\t',current_time,'\n')
