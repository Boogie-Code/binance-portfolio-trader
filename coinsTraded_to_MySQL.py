import config
import mysql.connector
from binance.client import Client
import datetime as dt

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')

mycursor = mydb.cursor()

spot = client.get_account()
balances = spot['balances']
for items in balances:
    if items['asset'] != 'ICN':
        if float(items['free'])+float(items['locked']) > 0:
            sql = '''INSERT IGNORE INTO spotSymbolsTraded (coin)
                        VALUES (%s)'''
            val = [items['asset']]
            mycursor.execute(sql,val)
sql2 = '''DELETE FROM spotSymbolsTraded WHERE coin = 'CTR' OR coin = 'EON' '''
mycursor.execute(sql2)
mydb.commit()
print('\tFinished checking spot coins with balances.')


isolated = client.get_isolated_margin_account()
assets = isolated['assets']
for items in assets:
    if float(items['baseAsset']['netAsset']) + float(items['quoteAsset']['netAsset']) != 0:
        sql = '''INSERT IGNORE INTO marginSymbolsTraded (ticker)
                VALUES (%s)'''
        val = [items['symbol']]
        mycursor.execute(sql,val)
mydb.commit()
print('\tFinished checking isolated coins with balances.')
current_time = dt.datetime.now()
print('FINISHED UPDATING COINS TRADED AT:\t\t',current_time,'\n')
