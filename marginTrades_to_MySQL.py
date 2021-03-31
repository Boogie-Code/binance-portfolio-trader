from binance.exceptions import BinanceAPIException
import config
import mysql.connector
import pprint
from binance.client import Client
import datetime as dt

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')

mycursor = mydb.cursor()

sql = '''SELECT * FROM marginSymbolsTraded'''
mycursor.execute(sql)
coinlist = mycursor.fetchall()

# ISOLATED TRADES UPDATE
try:
    for coin in coinlist:
        try:
            #print(coin[1])
            sql2 = '''SELECT max(trades_id) 
                    AS max_item 
                    FROM userMarginTrades 
                    WHERE pair = (%s)
                    AND isIsolated = 1 '''
            mycursor.execute(sql2,[coin[1]])
            last_trade = mycursor.fetchone()
            if last_trade[0] == None:
                last_trade = 1
            else:
                last_trade = int(last_trade[0]) + 1
            #print(last_trade)
            trades = client.get_margin_trades(symbol=coin[1], isIsolated='True', fromId=last_trade)
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
                print('New',coin[1],'trade')
                mydb.commit()
        except BinanceAPIException:
            print(coin[1],'fucked up your call bud')
            pass  
except Exception as e:
    print(e)
    pass

#   CROSS MARGIN TRADES
cross = client.get_margin_account()
if cross['totalNetAssetOfBtc'] == '0':
    print('\tNO CROSS MARGIN BALANCES, NOT CHECKING TRADES')
else:
    try:
        for coin in coinlist:
            try:
                # print(coin[1])
                sql2 = '''SELECT max(trades_id) 
                        AS max_item 
                        FROM userMarginTrades 
                        WHERE pair = (%s)
                        AND isIsolated = '0' '''
                mycursor.execute(sql2,[coin[1]])
                last_trade = mycursor.fetchone()
                if last_trade[0] == None:
                    last_trade = 1
                else:
                    last_trade = last_trade[0] + 1
                # print(last_trade)
                trades = client.get_margin_trades(symbol=coin, fromId=last_trade)
                for atrade in trades:
                    pprint.pp(atrade)
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
            except BinanceAPIException:
                print(coin[1])
                pass  
    except Exception as e:
        print(coin[1],e)
        pass

current_time = dt.datetime.now()
print('FINISHED UPDATING MARGIN TRADES AT:\t\t',current_time,'\n')
