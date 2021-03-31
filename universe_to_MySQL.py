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

mycursor = mydb.cursor(buffered=True)

def get_all_isolated_symbols():
    orders = client.get_all_isolated_margin_symbols()
    for items in orders:
        sql = '''INSERT IGNORE INTO marginSymbolsAll (symbol) VALUES (%s)'''
        val = [items['symbol']]
        mycursor.execute(sql,val)
        mydb.commit()
        # print(items['symbol'])

def get_all_coins():
    all_coins = client.get_all_tickers()
    for rows in all_coins:
        sql = '''INSERT IGNORE INTO spotSymbolsAll (symbol) VALUES (%s)'''
        val = [rows['symbol']]
        mycursor.execute(sql,val)
        mydb.commit()

get_all_isolated_symbols()
get_all_coins()

current_time = dt.datetime.now()
print('FINISHED UPDATING THE GALAXY AT:\t\t',current_time,'\n')
