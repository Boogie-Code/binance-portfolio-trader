from binance.exceptions import BinanceAPIException
import streamlit as st
import pandas as pd
import config
import mysql.connector
from binance.client import Client

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
list = ['',]
for coin in coinlist:
    list.append(coin[1])
    list.sort() 


st.sidebar.header('Which coin would you like to investigate,  my kind sir?')
option = st.sidebar.selectbox('',list)

if option == '':
    sql3 = '''  
        SELECT * FROM marginSymbolsTraded
    '''
    mycursor.execute(sql3)
    current_trades = pd.DataFrame(mycursor.fetchall())
    st.text(current_trades)

elif option == option:
    st.header(option)
    option2 = st.sidebar.selectbox('Next paramater here',[])
    sql2 = '''SELECT * FROM marginSymbolsTraded WHERE ticker = %s
    '''
    mycursor.execute(sql2,[option])
    prices = mycursor.fetchone()
    try:
        trades = pd.DataFrame(client.get_margin_trades(symbol=option, isIsolated='TRUE'))
    except BinanceAPIException:
        pass     
    st.text(prices)
    
    st.dataframe(trades)

