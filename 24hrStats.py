import config
import mysql.connector
from binance.client import Client
import datetime as dt

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db, auth_plugin='mysql_native_password')

mycursor = mydb.cursor()
    
def get_all_prices():
    delete_rows = """TRUNCATE TABLE 24hrStats"""
    mycursor.execute(delete_rows)
    mydb.commit()
    allprices = client.get_ticker()
    for items in allprices:
        list = (items['symbol'],
                float(items['priceChange']),
                float(items['priceChangePercent']),
                float(items['weightedAvgPrice']),
                float(items['prevClosePrice']),
                float(items['lastPrice']),
                float(items['openPrice']),
                float(items['highPrice']),
                float(items['lowPrice']),
                float(items['volume']),
                dt.datetime.fromtimestamp(items['openTime']/1000),
                dt.datetime.fromtimestamp(items['closeTime']/1000),
                items['firstId'],
                items['lastId'],
                items['count'])
        sql = ''' INSERT INTO binance_account.24hrStats (symbol,
            priceChange,
            priceChangePercent,
            weightedAvgPrice,
            prevClosePrice,
            lastPrice,
            openPrice,
            highPrice,
            lowPrice,
            volume,
            openTime,
            closeTime,
            firstId,
            lastId,
            count)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        val = list
        mycursor.execute(sql,val)
        mydb.commit( )
    time = dt.datetime.now()
    print('HOURLY ----------------','FINISHED UPDATING 24HR STATS AT:','\t',time,'\n')

get_all_prices()
