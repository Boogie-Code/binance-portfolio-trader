from logging import currentframe

from mysql.connector.errors import ProgrammingError
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

sql = '''SELECT * FROM marginSymbolsTraded'''
mycursor.execute(sql)
coinlist = mycursor.fetchall()

for symbol in coinlist:
    symbol = symbol[1]
    mycursor.execute('''SELECT 
        MAX(isolated_margin_current_id), 
        baseAsset_netAsset,
        USDValue_base,
        indexPrice 
        FROM marginBalancesIsolated 
        WHERE symbol = (%s)
        GROUP BY isolated_margin_current_id 
        ORDER BY isolated_margin_current_id DESC
        LIMIT 1''',
        [symbol])
    thing = mycursor.fetchone()
    open_balance = thing[1]
    usd_value = thing[2]
    lastPrice = thing[3]
    if open_balance > 0:
        if usd_value < 1:
            # print(symbol,'\tJust dust here\n')
            try:
                mycursor.execute('''UPDATE marginSymbolsTraded SET avgPricePaid = 0, profitloss = 0, side = NULL WHERE ticker = (%s)''',[symbol])
                mydb.commit()
            except ProgrammingError as e:
                print(e)
                continue
        else:
            # print(symbol,'LONG POSITION')
            mycursor.execute('''SELECT * 
                                FROM userMarginTrades 
                                WHERE pair = (%s)
                                AND side = 1 
                                ORDER BY dateOfTrade DESC''',
                                [symbol])
            list = mycursor.fetchall()
            totalPaid = 0
            totalBalance = 0
            balanceRemaining = open_balance
            for items in list:
                if balanceRemaining > 0:
                    # print('\t\t\tMatched trade...','Total paid:',items[6],"Quantity:",items[5],"Price:",round(items[6]/items[5],8))
                    totalPaid = totalPaid + items[6]
                    balanceRemaining = balanceRemaining - items[5]
                    totalBalance = totalBalance + items[5]
                if balanceRemaining < 0:
                    totalPaid = totalPaid - (-balanceRemaining/items[5])*items[6]
                    totalBalance = totalBalance - (-balanceRemaining/items[5])*items[5]
                    # print('\t\t\t\tPartially Matched trade...',"Matched amount:",round(items[5]+balanceRemaining,8),"Quantity in trade:",items[5])
                    balanceRemaining = 0                   
                if balanceRemaining == 0:
                    pass
            avgPrice = totalPaid/totalBalance
            profit = float(round(100*(1-(avgPrice/lastPrice)),3))            
            valueDelta = (totalPaid * profit)/100
            #print('\tTOTAL PAID:',totalPaid)
            #print('\tTOTAL BOUGHT:',totalBalance)
            #print('\tAVG PRICE:',avgPrice)
            #print('\tPROFIT/LOSS:',profit,'%\n')
            try:
                mycursor.execute('''UPDATE marginSymbolsTraded SET 
                                    avgPricePaid = (%s),
                                    profitloss = (%s), 
                                    side = 1, 
                                    valueDelta = (%s),
                                    valueAtRisk = (%s),
                                    lastPrice = (%s) 
                                    WHERE ticker = (%s)''',
                        [avgPrice,profit,valueDelta,totalPaid,lastPrice,symbol])
                mydb.commit()
            except ProgrammingError as e:
                print(e)
                continue
    if open_balance < 0:
        open_balance = -open_balance
        if usd_value > -1:
            # print(symbol,'\tJust dust here\n')
            try:
                mycursor.execute('''UPDATE marginSymbolsTraded SET avgPricePaid = 0, profitloss = 0, side = NULL WHERE ticker = (%s)''',[symbol])
                mydb.commit()
            except ProgrammingError as e:
                print(e)
                continue
        else:
            # print(symbol,'SHORT POSITION')
            mycursor.execute('''SELECT * 
                                FROM userMarginTrades 
                                WHERE pair = (%s)
                                AND side = 0 
                                ORDER BY dateOfTrade DESC''',
                                [symbol])
            list = mycursor.fetchall()
            totalPaid = 0
            totalBalance = 0
            balanceRemaining = open_balance
            for items in list:
                if balanceRemaining > 0:
                    # print('\t\t\tMatched trade...','Total paid:',items[6],"Quantity:",items[5],"Price:",round(items[6]/items[5],8))
                    totalPaid = totalPaid + items[6]
                    balanceRemaining = balanceRemaining - items[5]
                    totalBalance = totalBalance + items[5]
                if balanceRemaining < 0:
                    totalPaid = totalPaid - (-balanceRemaining/items[5])*items[6]
                    totalBalance = totalBalance - (-balanceRemaining/items[5])*items[5]
                    # print('\t\t\t\tPartially Matched trade...',"Matched amount:",round(items[5]+balanceRemaining,8),"Quantity in trade:",items[5])
                    balanceRemaining = 0                   
                if balanceRemaining == 0:
                    pass
            avgPrice = totalPaid/totalBalance
            profit = -float(round(100*(1-(avgPrice/lastPrice)),3))
            valueDelta = (totalPaid * profit)/100
            #print('\tTOTAL PAID:',totalPaid)
            #print('\tTOTAL SOLD:',totalBalance)
            #print('\tAVG PRICE:',avgPrice)
            #print('\tPROFIT/LOSS:',profit,'%\n')
            try:
                mycursor.execute('''UPDATE marginSymbolsTraded SET 
                                    avgPricePaid = (%s),
                                    profitloss = (%s), 
                                    side = 0, 
                                    valueDelta = (%s),
                                    valueAtRisk = (%s),
                                    lastPrice = (%s) 
                                    WHERE ticker = (%s)''',
                        [avgPrice,profit,valueDelta,totalPaid,lastPrice,symbol])
                mydb.commit()
            except ProgrammingError as e:
                print(e)
                continue
current_time = dt.datetime.now()
print('FINISHED FINDING AERAGE PRICES\t\t\t',current_time,'\n')
