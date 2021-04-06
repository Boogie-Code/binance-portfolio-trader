import time
import json
import hmac
import hashlib
import requests
import config
import pprint
import mysql.connector
import datetime as dt
import time
from urllib.parse import urljoin, urlencode

host = 'localhost'
user = 'root'
pw = config.DATABASE_PW
db = 'binance_account'
mydb = mysql.connector.connect(host=host,user=user,password=pw,database=db,auth_plugin='mysql_native_password')
mycursor = mydb.cursor()

sql = '''SELECT * FROM spotSymbolsAll'''
mycursor.execute(sql)
coinlist = mycursor.fetchall()

API_KEY = config.API_KEY
SECRET_KEY = config.API_SECRET
BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY}

class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"
        super().__init__(message)
PATH =  '/api/v1/time'
params = None

timestamp = int(time.time() * 1000)

url = urljoin(BASE_URL, PATH)
r = requests.get(url, params=params)
if r.status_code == 200:
    # print(json.dumps(r.json(), indent=2))
    data = r.json()
    print(f"diff={timestamp - data['serverTime']}ms")
else:
    raise BinanceException(status_code=r.status_code, data=r.json())


for symbol in coinlist:
    print(symbol[1])
    time.sleep(1/4)
    symbol = symbol[1]
    PATH = '/sapi/v1/margin/transfer'
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': symbol,
        'recvWindow': 10000,
        'startTime': 1517332172386,
        'timestamp': timestamp}
    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    # print(params)
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        # print(json.dumps(data))
        for rows in data['rows']:
            # print(rows)
            list = [dt.datetime.fromtimestamp(rows['timestamp']/1000),
                    symbol,
                    rows['asset'],
                    rows['amount'],
                    rows['status'],
                    rows['txId'],
                    rows['transFrom']]
            print(list)
            sql = '''INSERT INTO marginTransfersIsolated (timestamp,isolatedAccount,asset,amount,status,txId,transferFrom) VALUE (%s,%s,%s,%s,%s,%s,%s)'''
            val = list
            mycursor.execute(sql,val)
            mydb.commit()
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())