import config
import mysql.connector
from binance.exceptions import BinanceAPIException
from binance.client import Client
import datetime as dt
import time, pprint

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')

mycursor = mydb.cursor(buffered=True)

sql2 = '''SELECT * FROM spotSymbolsAll'''
mycursor.execute(sql2)

spotSymbols = mycursor.fetchall()

#  SPOT TRADES INITIALIZATION
for coins in spotSymbols:
    print(coins[1])
    time.sleep(1/2)
    try:
        spottrade = client.get_my_trades(symbol=coins[1])    #If more than 500 trades per coin, need to fix this
        for eachtrade in spottrade:
            # pprint.pp(eachtrade)
            sql = '''INSERT INTO userSpotTrades (
                pair,
                trades_id,
                orderId,
                side,
                pricePaid,
                qty,
                totalPrice,
                dateOfTrade,
                isMaker,
                commission,
                commissionAsset)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)'''
            val = [eachtrade['symbol'],
                eachtrade['id'],
                eachtrade['orderId'],
                eachtrade['isBuyer'],
                eachtrade['price'],
                eachtrade['qty'],
                eachtrade['quoteQty'],
                dt.datetime.fromtimestamp(eachtrade['time']/1000),
                eachtrade['isMaker'],
                eachtrade['commission'],
                eachtrade['commissionAsset']       
                ]
            mycursor.execute(sql,val)
            mydb.commit()
            print(coins[1],'record insertion.')
    except BinanceAPIException as e:
        print(e)
        continue

current_time = dt.datetime.now()
print('FINISHED INITIALIZING TRADES AT:\t\t',current_time)

#  SPOT ORDERS INITIALIZATION
for row in spotSymbols:
    print(row[1])
    time.sleep(1/2)
    try:
        orders = client.get_all_orders(symbol=row[1])
        for thing in orders:
            # print(thing)
            list = [thing['symbol'],
                    thing['orderId'], 
                    thing['clientOrderId'],
                    thing['price'],
                    thing['origQty'],
                    thing['executedQty'],
                    thing['cummulativeQuoteQty'],
                    thing['status'],
                    thing['timeInForce'],
                    thing['type'],
                    thing['side'],
                    thing['stopPrice'],
                    thing['icebergQty'], 
                    dt.datetime.fromtimestamp(thing['time']/1000),
                    dt.datetime.fromtimestamp(thing['updateTime']/1000),
                    thing['isWorking'],
                    thing['origQuoteOrderQty']
                    ]
            sql = """ INSERT INTO userSpotOrders 
                            (symbol,
                            orderId,
                            clientOrderId,
                            price,
                            origQty,
                            executedQty,
                            cumulativeQuoteQty,
                            status,
                            timeInForce,
                            type,
                            side,
                            stopPrice,
                            icebergQty,
                            time,
                            updatedTime,
                            isWorking,
                            origQuoteOrderQty)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
            val = list
            mycursor.execute(sql,val)
            print(thing['symbol'],'Record inserted into table.')
            mydb.commit()  
    except BinanceAPIException as e:
        print(e)
        continue

current_time = dt.datetime.now()
print('FINISHED INITIALIZING SPOT ORDERS AT:\t\t',current_time)