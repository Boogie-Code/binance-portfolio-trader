from logging import error
from binance.exceptions import BinanceAPIException
import mysql.connector
from binance.client import Client
import config, json, csv
import pandas as pd
from datetime import datetime

current_time = datetime.now()

host = '127.0.0.1'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

client = Client(config.API_KEY, config.API_SECRET)                              

mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')
mycursor = mydb.cursor()

# def create_list_of_coins():
isolated_coins_traded = []
sql = '''SELECT * FROM marginSymbolsTraded'''
mycursor.execute(sql)
for items in mycursor.fetchall():
        isolated_coins_traded.append(items[1])

# def add_current_isolated_balances():
try:
    for v in isolated_coins_traded:
        try:
            x = client.get_isolated_margin_account(symbols=v, isIsolated='True')
            current_time = datetime.now()
            list = [x['assets'][0]['baseAsset']['asset'],
                x['assets'][0]['baseAsset']['borrowEnabled'],
                x['assets'][0]['baseAsset']['borrowed'],
                x['assets'][0]['baseAsset']['free'],
                x['assets'][0]['baseAsset']['interest'],
                x['assets'][0]['baseAsset']['locked'],
                x['assets'][0]['baseAsset']['netAsset'],
                x['assets'][0]['baseAsset']['netAssetOfBtc'],
                x['assets'][0]['baseAsset']['repayEnabled'],
                x['assets'][0]['baseAsset']['totalAsset'],
                x['assets'][0]['quoteAsset']['asset'],
                x['assets'][0]['quoteAsset']['borrowEnabled'],
                x['assets'][0]['quoteAsset']['borrowed'],
                x['assets'][0]['quoteAsset']['free'],
                x['assets'][0]['quoteAsset']['interest'],
                x['assets'][0]['quoteAsset']['locked'],
                x['assets'][0]['quoteAsset']['netAsset'],
                x['assets'][0]['quoteAsset']['netAssetOfBtc'],
                x['assets'][0]['quoteAsset']['repayEnabled'],
                x['assets'][0]['quoteAsset']['totalAsset'],
                x['assets'][0]['symbol'],
                x['assets'][0]['isolatedCreated'],
                x['assets'][0]['marginRatio'],
                x['assets'][0]['indexPrice'],
                x['assets'][0]['liquidatePrice'],
                x['assets'][0]['liquidateRate'],
                x['assets'][0]['tradeEnabled'],
                current_time,
                (float((x['assets'][0]['baseAsset']['netAsset'])) * float((x['assets'][0]['indexPrice']))),
                (float((x['assets'][0]['baseAsset']['netAsset'])) * float((x['assets'][0]['indexPrice'])))
                    +   float((x['assets'][0]['quoteAsset']['netAsset'])),
                round(((float((x['assets'][0]['quoteAsset']['netAsset'])))
                    /   ((float((x['assets'][0]['baseAsset']['netAsset'])) * float((x['assets'][0]['indexPrice'])))
                        +   float((x['assets'][0]['quoteAsset']['netAsset'])) + 0.000001))-0.9999999,2)*(-1.0)   
                ]
            sql = """ INSERT INTO marginBalancesIsolated (
                                baseAsset_asset,
                                baseAsset_borrowEnabled,
                                baseAsset_borrowed,
                                baseAsset_free,
                                baseAsset_interest,
                                baseAsset_locked,
                                baseAsset_netAsset,
                                baseAsset_netAssetOfBtc,
                                baseAsset_repayEnabled,
                                baseAsset_totalAsset,
                                quoteAsset_asset,
                                quoteAsset_borrowEnabled,
                                quoteAsset_borrowed,
                                quoteAsset_free,
                                quoteAsset_interest,
                                quoteAsset_locked,
                                quoteAsset_netAsset,
                                quoteAsset_netAssetOfBtc,
                                quoteAsset_repayEnabled,
                                quoteAsset_totalAsset,
                                symbol,
                                isolatedCreated,
                                marginRatio, 
                                indexPrice, 
                                liquidatePrice, 
                                liquidateRate,
                                tradeEnabled,
                                updated_date,
                                USDValue_base,
                                totalUSDValue,
                                leverageAmount) 
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""    
            val = list
            if float(float(list[9]) + float(list[19])) != 0:
                mycursor.execute(sql,val)    
            else:
                pass
        except IndexError:
            continue
except error:
    print(error)
        
mydb.commit()

current_time = datetime.now()   
print('MARGIN BALANCES UPDATED AT:\t\t\t',current_time,'\n')
