from logging import error
from binance.exceptions import BinanceAPIException
import config
import mysql.connector
import time
from binance.client import Client
import datetime as dt

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')

mycursor = mydb.cursor()

sql = '''SELECT * FROM marginSymbolsAll'''
mycursor.execute(sql)
coinlist = mycursor.fetchall()

# ISOLATED TRADE INITIALIZATION
try:
    for coin in coinlist:
        print("CHECKING:\t",coin[1])
        time.sleep(1)
        try:
            trades = client.get_margin_trades(symbol=coin[1], isIsolated='True')
            for atrade in trades:
                # print(atrade)
                sql = '''INSERT INTO userMarginTrades(
                    pair,
                    trades_id,
                    orderId,
                    pricePaid,
                    qty,
                    totalPrice,
                    dateOfTrade,
                    side,
                    isMaker,
                    isIsolated,
                    commission,
                    commissionAsset)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                val = [atrade['symbol'],
                        atrade['id'],
                        atrade['orderId'],
                        atrade['price'],
                        atrade['qty'],
                        float(atrade['qty']) * float(atrade['price']),
                        dt.datetime.fromtimestamp(atrade['time']/1000),
                        atrade['isBuyer'],
                        atrade['isMaker'],
                        atrade['isIsolated'],
                        atrade['commission'],
                        atrade['commissionAsset']
                        ]    
                mycursor.execute(sql,val)
                mydb.commit()
            print(len(trades),coin[1],'record(s) inserted.')
        except BinanceAPIException as e:
            print(coin[1],e)
            continue  
except Exception as e:
    print(coin,e)
    pass
    print(coin,'FOOL!!')

# CROSS MARGIN TRADE INITIALIZATION
try:
    for coin in coinlist:
        print('CHECKING:\t',coin[1])
        time.sleep(1)
        try:
            trades = client.get_margin_trades(symbol=coin[1])
            for atrade in trades:
                # print(atrade)
                sql = '''INSERT INTO userMarginTrades(
                    pair,
                    trades_id,
                    orderId,
                    pricePaid,
                    qty,
                    totalPrice,
                    dateOfTrade,
                    side,
                    isMaker,
                    isIsolated,
                    commission,
                    commissionAsset)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        '''
                val = [atrade['symbol'],
                        atrade['id'],
                        atrade['orderId'],
                        atrade['price'],
                        atrade['qty'],
                        float(atrade['qty']) * float(atrade['price']),
                        dt.datetime.fromtimestamp(atrade['time']/1000),
                        atrade['isBuyer'],
                        atrade['isMaker'],
                        atrade['isIsolated'],
                        atrade['commission'],
                        atrade['commissionAsset']
                        ]    
                mycursor.execute(sql,val)
                mydb.commit()
                print(len(trades),coin[1],'record(s) inserted.')
        except BinanceAPIException as e:
            print(coin[1],e)
            pass  
except Exception as e:
    print(coin,e)
    pass
    print(coin,'FOOL!!')