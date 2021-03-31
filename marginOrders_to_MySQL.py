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

sql = '''SELECT * FROM marginSymbolsTraded'''
mycursor.execute(sql)
coinlist = mycursor.fetchall()
# print(coinlist)

#   CROSS-MARGIN ORDERS UPDATE
cross = client.get_margin_account()
#print(cross['totalNetAssetOfBtc'])
if cross['totalNetAssetOfBtc'] == '0':
    print('\tNO CROSS MARGIN BALANCES, NOT CHECKING ORDERS')
else:
    for row in coinlist:
        try:
            sql2 = '''SELECT max(orderId) 
                AS max_item 
                FROM userMarginOrders 
                WHERE symbol = (%s)
                AND (status <> "NEW")
                AND (isIsolated = '0') 
            '''
            mycursor.execute(sql2,[row[1]])
            maxOrderId = mycursor.fetchone()
            print(row[1])
            trades = client.get_all_margin_orders(symbol=row[1], isIsolated='FALSE', orderId=maxOrderId[0])
            for thing in trades:
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
                            AS new
                        ON DUPLICATE KEY UPDATE
                            executedQty = new.executedQty,
                            cumulativeQuoteQty = new.cumulativeQuoteQty,
                            status = new.status,
                            updatedTime = new.updatedTime
                            """
                val = list
                mycursor.execute(sql,val)
                #print(thing['symbol'],'Record inserted/updated in table.')
                mydb.commit()  
        except BinanceAPIException as e:
            print(e)
            continue

#   ISOLATED ORDERS UPDATE
for row in coinlist:
    try:    # SELECT THE LOWEST ORDERID OF OPEN ORDERS TO START LOOKING FOR NEW/UPDATED TRADES
        sql2 = '''SELECT min(orderId) 
            AS min_item 
            FROM userMarginOrders 
            WHERE symbol = (%s)
            AND (status = "NEW")
            AND (isIsolated = '1') 
        '''
        mycursor.execute(sql2,[row[1]])
        maxOrderId = mycursor.fetchone()
        #print(row[1],maxOrderId[0])
        maxOrderId = (maxOrderId[0])
        if maxOrderId == None:
            try:            #  In case there are no "NEW"/Open Orders, select the maximum orderId in the table to start looking for new orders from
                sql2 = '''SELECT max(orderId) 
                    AS max_item 
                    FROM userMarginOrders 
                    WHERE symbol = (%s)
                    AND (status <> "NEW")
                    AND (isIsolated = '1') 
                '''
                mycursor.execute(sql2,[row[1]])
                maxOrderId = mycursor.fetchone()
                #print(row[1],type(maxOrderId[0]))
                if maxOrderId[0] == None:
                    maxOrderId = [1,]
                    #print(maxOrderId)
                maxOrderId = (maxOrderId[0] +1)
                # print(maxOrderId)
                trades = client.get_all_margin_orders(symbol=row[1], isIsolated='TRUE', orderId=maxOrderId)
                for x in trades:
                    list = [x['symbol'],
                            x['orderId'], 
                            x['clientOrderId'],
                            x['price'],
                            x['origQty'],
                            x['executedQty'],
                            x['cummulativeQuoteQty'],
                            x['status'],
                            x['timeInForce'],
                            x['type'],
                            x['side'],
                            x['stopPrice'],
                            x['icebergQty'], 
                            dt.datetime.fromtimestamp(x['time']/1000),
                            dt.datetime.fromtimestamp(x['updateTime']/1000),
                            x['isWorking'],
                            x['isIsolated']
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
                                AS new
                                ON DUPLICATE KEY UPDATE
                                    executedQty = new.executedQty,
                                    cumulativeQuoteQty = new.cumulativeQuoteQty,
                                    status = new.status,
                                    updatedTime = new.updatedTime
                                """
                    val = list
                    mycursor.execute(sql,val)
                    mydb.commit()
                    #print(row[1],'Record inserted/updated into table.')
            except BinanceAPIException as e:
                print(e)
                continue       
        else:
            #print(maxOrderId)
            trades = client.get_all_margin_orders(symbol=row[1], isIsolated='TRUE', orderId=maxOrderId)
            for x in trades:
                list = [x['symbol'],
                        x['orderId'], 
                        x['clientOrderId'],
                        x['price'],
                        x['origQty'],
                        x['executedQty'],
                        x['cummulativeQuoteQty'],
                        x['status'],
                        x['timeInForce'],
                        x['type'],
                        x['side'],
                        x['stopPrice'],
                        x['icebergQty'], 
                        dt.datetime.fromtimestamp(x['time']/1000),
                        dt.datetime.fromtimestamp(x['updateTime']/1000),
                        x['isWorking'],
                        x['isIsolated']
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
                            AS new
                            ON DUPLICATE KEY UPDATE
                                executedQty = new.executedQty,
                                cumulativeQuoteQty = new.cumulativeQuoteQty,
                                status = new.status,
                                updatedTime = new.updatedTime
                            """
                val = list
                mycursor.execute(sql,val)
                mydb.commit()  
                #print(row[1],'Record inserted/updated into table.')
    except BinanceAPIException as f:
        print(f)

current_time = dt.datetime.now()        
print('FINISHED UPDATING MARGIN ORDERS AT:\t\t',current_time,'\n')
