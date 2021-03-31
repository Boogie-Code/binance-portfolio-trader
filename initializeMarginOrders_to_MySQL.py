import config
import mysql.connector
from binance.exceptions import BinanceAPIException
from binance.client import Client
import datetime as dt
import time

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')

mycursor = mydb.cursor(buffered=True)

sql = '''SELECT * FROM marginSymbolsAll'''
mycursor.execute(sql)
coinlist = mycursor.fetchall()

#   NON-ISOLATED ORDERS INITIALIZATION
for row in coinlist:
    print(row[1])
    time.sleep(1)
    try:
        trades = client.get_all_margin_orders(symbol=row[1])
        for thing in trades:
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
                    thing['isIsolated']
                    ]
            sql = """ INSERT INTO userMarginOrders 
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
                            isIsolated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
            val = list
            mycursor.execute(sql,val)
            print(thing['symbol'],'Record inserted into table.')
            mydb.commit()  
    except BinanceAPIException as e:
        print(e)
        continue

#   ISOLATED ORDERS INITIALIZATION
for row in coinlist:
    print(row[1])
    time.sleep(1)
    try:
        trades = client.get_all_margin_orders(symbol=row[1], isIsolated='TRUE')
        for thing in trades:
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
                    thing['isIsolated']
                    ]
            sql = """ INSERT INTO userMarginOrders 
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
                            isIsolated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
            val = list
            mycursor.execute(sql,val)
            print(thing['symbol'],'Record inserted into table.')
            mydb.commit()  
    except BinanceAPIException as e:
        print(e)
        continue
