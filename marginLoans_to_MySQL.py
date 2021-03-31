from logging import error
from binance.client import Client
import config, csv, mysql.connector, sys
import datetime as dt
from datetime import timezone

#   Define variables for the database 'binance_account'
host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'

#   Connect to Binance
client = Client(config.API_KEY, config.API_SECRET)                              

#   Connect to MySQL database 'binance_account'
mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')
mycursor = mydb.cursor()


#   Call the latest date in the table 'marginBorrowed' and 
#   create a variable for binance.Client called 'start_date' to start searching from.
#   This will allow the code to skip items already in the table.
try:
    mycursor.execute('''SELECT max(marginBorrowTimestamp) as max_items FROM marginBorrowIsolated;''')       
    start_time = int(dt.datetime.timestamp(mycursor.fetchone()[0]))*1000 + 28800    
except:
    if error:
        start_time = 1
        print('No information in the table yet')
        print(error)
        pass

#   Create an empty list and then append each row in 'isolated_coins_traded.csv' into the list
isolated_coins_traded = []
sql = '''SELECT * FROM marginSymbolsTraded'''
mycursor.execute(sql)
for items in mycursor.fetchall():
            isolated_coins_traded.append(items[1])

#   Check for new borrowed amounts 
print('\tCHECKING LOANS...')                         #If code is not working try resetting startTime in the binance call to '1'
for k in ['BUSD','USDT']:
    try:
        for v in isolated_coins_traded:
            try:                
                x = client.get_margin_loan_details(asset=k, isolatedSymbol=str(v), startTime=start_time,size=100)   #When populating empty database, startTime=1
                # print('... checking for new entries in',k,v)   # For troubleshooting
                for items in x['rows']:
                    list = [dt.datetime.fromtimestamp(items['timestamp']/1000),
                            items['txId'],
                            items['asset'],
                            items['principal'],
                            items['status'],
                            items['isolatedSymbol']
                            ]
                    sql = """INSERT IGNORE INTO marginBorrowIsolated 
                               (marginBorrowTimestamp,
                                marginBorrowTxId,
                                marginBorrowAsset,
                                marginBorrowPrincipal,
                                marginBorrowStatus,
                                marginBorrowIsolatedSymbol) 
                            VALUES (%s, %s,%s,%s,%s,%s)                                                
                        """
                    val = list
                    # print(list)
                # if list[4] == 'CONFIRMED':    # Comment and tab in if you want to ignore FAILED entries
                    mycursor.execute(sql,val)
                    print(items['isolatedSymbol'],'Record inserted into table.')
            except IndexError as e:
                print(e)
                continue
    except IndexError as e:
        print(e)
        continue

print('\tCHECKING REPAYMENTS.... ')
for k in ['BUSD','USDT']:
    try:
        for v in isolated_coins_traded:
            try:                
                x = client.get_margin_repay_details(asset=k, isolatedSymbol=str(v), startTime=start_time,size=100)    #Once all records are collected, can adjust the start time to optimize the run time
                # print('... checking for new entries in',k,v)
                for items in x['rows']:
                    list = [dt.datetime.fromtimestamp(items['timestamp']/1000),
                            items['amount'],
                            items['interest'],                            
                            items['txId'],
                            items['asset'],
                            items['principal'],
                            items['status'],
                            items['isolatedSymbol']
                            ]
                    sql = """INSERT IGNORE INTO marginBorrowIsolated 
                               (marginBorrowTimestamp,
                                marginBorrowTotalRepaid,
                                marginBorrowInterestRepaid,
                                marginBorrowTxId,
                                marginBorrowAsset,
                                marginBorrowPrincipalRepaid,
                                marginBorrowStatus,
                                marginBorrowIsolatedSymbol) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)                                                       
                        """
                    val = list
                    # print(list)
                    if list[6] == 'CONFIRMED':
                        mycursor.execute(sql,val)
                        print(items['isolatedSymbol'],'Record inserted into table.')
            except IndexError as e:
                print(e)
                continue
    except IndexError as e:
        print(e)
        continue
mydb.commit()
current_time = dt.datetime.now()
print('FINSIHED CHECKING LOANS/REPAYMENTS AT:\t\t',current_time,'\n')
