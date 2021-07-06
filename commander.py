import sqlite3
import csv
from decimal import Decimal
from datetime import datetime
from datetime import timedelta
import dateutil.parser

deposit_realdate=0

database = sqlite3.connect("database.db")
dbcursor = database.cursor()

dbcursor.execute("CREATE TABLE IF NOT EXISTS deposit (tid varchar(100), date DATE, asset varchar(6), amount_in DOUBLE(10))")
dbcursor.execute("CREATE TABLE IF NOT EXISTS buy (tid varchar(100), date DATE, asset_in varchar(6), amount_in DOUBLE(10), amount_eur DOUBLE(10), transfer boolean not null default 0,deposit boolean not null default 0)")
dbcursor.execute("CREATE TABLE IF NOT EXISTS sell (tid varchar(100), date DATE, asset_in varchar(6), amount_in DOUBLE(10), amount_eur DOUBLE(10), transfer boolean not null default 0, withdraw boolean not null default 0)")
dbcursor.execute("CREATE TABLE IF NOT EXISTS transactions (tid_buy varchar(100),tid_sell varchar(100), date_buy DATE, date_sell DATE, asset varchar(6), amount DOUBLE(10), amount_eur_buy DOUBLE(10), amount_eur_sell DOUBLE(10),date_diff DATE)")

dataptr=0

with open('bitpanda.csv') as csvfile:
    csv_reader_object = csv.reader(csvfile, delimiter=',')
    for row in csv_reader_object:
        dataptr+=1
        if dataptr > 7:
            if row[2] == "deposit":
                dbcursor.execute("SELECT tid FROM deposit where tid='"+ row[0]+"'");
                result = dbcursor.fetchall()
                print (result)
                if result==[]:
                    print("is zero")
                    if row[7] == 'EUR':
                        continue
                    #Check if asset fee payed with same currencency, decrease fee
                    #if row[7] == row[13]:
                    #    if row[7] != 'EUR':
                    #        print("decrease fee: "+row[6] + "-" + row[12])
                    #        row[6]= str(Decimal(row[6])-Decimal(row[12]))
                    dbcursor.execute("INSERT INTO deposit (tid,date,asset,amount_in) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"')")
                    if deposit_realdate == 0:
                        #Handle deposit like bought 1 year before in anyway, so set old date
                        dbcursor.execute("INSERT INTO buy (tid,date,asset_in,amount_in,amount_eur,deposit) VALUES('"+ row[0] + "', '2010-05-22T12:58:47+02:00', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"','1')")
                    else:
                        dbcursor.execute("INSERT INTO buy (tid,date,asset_in,amount_in,amount_eur,deposit) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"','1')")
                else:
                    print("is not zero")
            if row[2] == "buy":
                dbcursor.execute("SELECT tid FROM buy where tid='"+ row[0]+"'");
                result = dbcursor.fetchall()
                print (result)
                if result==[]:
                    print("is zero")
                    if row[7] == row[13]:
                        if row[7] != 'EUR':
                            print("decrease fee: "+row[6] + "-" + row[12])
                            row[6]= str(Decimal(row[6])-Decimal(row[12]))
                    dbcursor.execute("INSERT INTO buy (tid,date,asset_in,amount_in,amount_eur) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"')")
                else:
                    print("is not zero")
            if row[2] == "sell":
                dbcursor.execute("SELECT tid FROM sell where tid='"+ row[0]+"'");
                result = dbcursor.fetchall()
                print (result)
                if result==[]:
                    print("is zero")
                    if row[7] == row[13]:
                        if row[7] != 'EUR':
                                print("decrease fee: "+row[6] + "-" + row[12])
                                row[6]= str(Decimal(row[6])+Decimal(row[12]))

                    dbcursor.execute("INSERT INTO sell (tid,date,asset_in,amount_in,amount_eur) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"')")
                else:
                    print("is not zero")
            if row[2] == "withdrawal":
                dbcursor.execute("SELECT tid FROM sell where tid='"+ row[0]+"'");
                result = dbcursor.fetchall()
                print (result)
                if result==[]:
                    print("is zero")
                    if row[7] == 'EUR':
                        continue
                    if row[7] == row[13]:
                        if row[7] != 'EUR':
                            if Decimal(row[6]) != 0:
                                print("decrease fee: "+row[6] + "-" + row[12])
                                row[6]= str(Decimal(row[6])+Decimal(row[12]))
                            elif Decimal(row[12]) != 0:
                                row[6]=row[12]
                            else:
                                continue
                    dbcursor.execute("INSERT INTO sell (tid,date,asset_in,amount_in,amount_eur,withdraw) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"', 1)")
                else:
                    print("is not zero")
            if row[2] == "transfer":
                if row[3] == "outgoing":
                    dbcursor.execute("SELECT tid FROM sell where tid='"+ row[0]+"'");
                if row[3] == "incoming":
                    dbcursor.execute("SELECT tid FROM buy where tid='"+ row[0]+"'");
                result = dbcursor.fetchall()
                print (result)
                if result==[]:
                    print("is zero")
                    if row[7] == 'EUR':
                        continue
                    if row[7] == row[13]:
                        if row[7] != 'EUR':
                            print("decrease fee: "+row[6] + "-" + row[12])
                            row[6]= str(Decimal(row[6])-Decimal(row[12]))
                    if row[3] == "outgoing":
                        dbcursor.execute("INSERT INTO sell (tid,date,asset_in,amount_in,amount_eur,transfer) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"',1)")
                    if row[3] == "incoming":
                        dbcursor.execute("INSERT INTO buy (tid,date,asset_in,amount_in,amount_eur,transfer) VALUES('"+ row[0] + "', '" + row[1] + "', '" + row[7] + "', '" + row[6] +"', '" + row[4] +"',1)")
                else:
                    print("is not zero")     
               
                
database.commit()
dbcursor.execute("SELECT SUM(amount_in) FROM buy where asset_in='XRP'");
result = dbcursor.fetchall()
print (result[0][0])
btc=result[0][0]
dbcursor.execute("SELECT SUM(amount_in) FROM sell where asset_in='XRP'");
result = dbcursor.fetchall()
print (result[0][0])
btc-=result[0][0]
print(btc)
dbcursor.execute("SELECT * FROM sell order by date asc");
sell = dbcursor.fetchall()
print("Sell0=")
print (sell[0])
for sellelem in sell:
    print("Sellelem:")
    print(sellelem)
    dbcursor.execute("SELECT tid_sell FROM transactions where tid_sell='" + sellelem[0] + "' order by rowid asc");
    result = dbcursor.fetchall()
    if result == []:
      if sellelem[2] != "EUR":
        dbcursor.execute("SELECT * FROM buy where asset_in='" + sellelem[2] + "' order by rowid asc");
        buy = dbcursor.fetchall()
        print(buy)
        dbcursor.execute("SELECT * FROM transactions where asset='" + sellelem[2] + "' order by date_sell asc");
        sumspend = dbcursor.fetchall()
        print(sumspend)
        if sumspend == []:
            print("Sell - Buy" + sellelem[2])
            print(sellelem[3] - buy[0][3])
            if Decimal(buy[0][3] - sellelem[3]) == 0:
                print("Write to database")
                dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buy[0][0] + "', '" + sellelem[0] + "', '" + buy[0][1] + "', '" + sellelem[1] + "', '" + str(buy[0][2]) + "', '"  + str(sellelem[3]) + "', '" + str(buy[0][4]) + "', '" + str(sellelem[4]) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buy[0][1])) + "')") 
            elif Decimal(buy[0][3] - sellelem[3]) > 0:
                priceperpiece=buy[0][4]/buy[0][3]
                sellpriceperpiece=sellelem[4]/sellelem[3]
                dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buy[0][0] + "', '" + sellelem[0] + "', '" + buy[0][1] + "', '" + sellelem[1] + "', '" + str(buy[0][2]) + "', '"  + str(sellelem[3]) + "', '" + str(priceperpiece*sellelem[3]) + "', '" + str(sellelem[4]) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buy[0][1])) + "')")
            elif Decimal(buy[0][3] - sellelem[3]) < 0:
                amount = sellelem[3]
                sellprice = sellelem[4]
                priceperpiece=amount/sellprice
                index = 0
                while amount > 0:
                    if Decimal(amount - buy[index][3]) < 0:
                        dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buy[index][0] + "', '" + sellelem[0] + "', '" + buy[index][1] + "', '" + sellelem[1] + "', '" + str(buy[index][2]) + "', '"  + str(buy[index][3]) + "', '" + str(buy[index][4]) + "', '" + str(priceperpiece*buy[index][3]) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buy[index][1])) + "')")
                        index+=1
                        amount-=round(buy[index][3],10)
                        print("amountleft: " + str(amount))
                    elif Decimal(amount - buy[index][3]) >= 0:
                        dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buy[index][0] + "', '" + sellelem[0] + "', '" + buy[index][1] + "', '" + sellelem[1] + "', '" + str(buy[index][2]) + "', '"  + str(round(amount,10)) + "', '" + str((buy[index][4]/buy[index][3])*amount) + "', '" + str(priceperpiece*amount) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buy[index][1])) + "')")
                        amount=0
        else:
            dbcursor.execute("SELECT SUM(amount) FROM transactions where asset='" + sellelem[2] + "' order by date_sell asc");
            sumspend = dbcursor.fetchall()
            print("Sum spend of " + sellelem[2])
            print(sumspend)
            amount = sumspend[0][0]
            overleft=0
            print(sellelem)
            sellperpiece=sellelem[4]/sellelem[3]
            for buyelem in buy:
                print("buyelement:")
                print(buyelem)
                
                if overleft > 0:
                    print("overleft")
                    priceperpiece=buyelem[4]/buyelem[3]
                    if (buyelem[3] - overleft)  >= 0:
                        dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buyelem[0] + "', '" + sellelem[0] + "', '" + buyelem[1] + "', '" + sellelem[1] + "', '" + str(buyelem[2]) + "', '"  + str(round(overleft,10)) + "', '" + str(priceperpiece*overleft) + "', '" + str(overleft*sellperpiece) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buyelem[1])) + "')")
                        overleft=0
                    elif (buyelem[3] - overleft)  < 0:
                        dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buyelem[0] + "', '" + sellelem[0] + "', '" + buyelem[1] + "', '" + sellelem[1] + "', '" + str(buyelem[2]) + "', '"  + str(round(buyelem[3],10)) + "', '" + str(priceperpiece*buyelem[3]) + "', '" + str(buyelem[3]*sellperpiece) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buyelem[1])) + "')")
                        overleft-=buyelem[3]
                elif buyelem[3] - amount  < 0:
                    amount -= buyelem[3]
                    print("Skip element" + str(buyelem[3] - amount))
                elif (buyelem[3] - amount)  == 0:
                    amount = 0
                    overleft = float(sellelem[3])
                    print("Skip element" + str(buyelem[3] - amount))
                elif buyelem[3] - amount  > 0:
                    if (buyelem[3] - amount - sellelem[3])  >= 0:
                        priceperpiece=buyelem[4]/buyelem[3]
                        dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buyelem[0] + "', '" + sellelem[0] + "', '" + buyelem[1] + "', '" + sellelem[1] + "', '" + str(buyelem[2]) + "', '"  + str(round(sellelem[3],10)) + "', '" + str(priceperpiece*sellelem[3]) + "', '" + str(sellelem[4]) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buyelem[1])) + "')")
                        amount=0
                    if (buyelem[3] - amount - sellelem[3])  < 0:
                        priceperpiece=buyelem[4]/buyelem[3]
                        dbcursor.execute("INSERT INTO transactions (tid_buy,tid_sell,date_buy,date_sell,asset,amount,amount_eur_buy,amount_eur_sell,date_diff) VALUES('"+ buyelem[0] + "', '" + sellelem[0] + "', '" + buyelem[1] + "', '" + sellelem[1] + "', '" + str(buyelem[2]) + "', '"  + str(round(round(buyelem[3],10)-round(amount,10),10)) + "', '" + str(priceperpiece*(buyelem[3]-amount)) + "', '" + str((buyelem[3]-amount)*sellperpiece) + "', '" + str(dateutil.parser.parse(sellelem[1])-dateutil.parser.parse(buyelem[1])) + "')")
                        overleft = round(sellelem[3],10)-round(buyelem[3],10)+round(amount,10);
                        amount=0
                    
                if amount == 0:
                    if overleft == 0:
                        break
                    
        dbcursor.execute("SELECT SUM(amount) FROM transactions where asset='" + sellelem[2] + "' order by date_sell asc");
        sumspend = dbcursor.fetchall()
        print(sumspend[0])

dbcursor.execute("SELECT * FROM transactions");
sumspend = dbcursor.fetchall()
print("Full Transaction Database:")
print(sumspend)

database.commit()

dbcursor.execute("SELECT SUM(amount_in) FROM buy where asset_in='XRP'");
result = dbcursor.fetchall()
print (result[0][0])
btc=result[0][0]
dbcursor.execute("SELECT SUM(amount) FROM transactions where asset='XRP'");
result = dbcursor.fetchall()
print (result[0][0])
btc-=result[0][0]
print(btc)

dbcursor.execute("SELECT * FROM transactions");
sumspend = dbcursor.fetchall()
y2019=0
y2020=0
y2021=0

print("Transaction less 1 year:")
for elem in sumspend:
    selldate=dateutil.parser.parse(elem[3])
    buydate=dateutil.parser.parse(elem[2])
    if selldate-buydate < timedelta(days=366):
        print(dateutil.parser.parse(elem[3])-dateutil.parser.parse(elem[2]))
        print(elem)
        if selldate.year==2021:
            y2021+=elem[7]-elem[6]
        elif selldate.year==2020:
            y2020+=elem[7]-elem[6]
        elif selldate.year==2019:
            y2019+=elem[7]-elem[6]

print("Year 2019: " + str(y2019))
print("Year 2020: " + str(y2020))
print("Year 2021: " + str(y2021))

dbcursor.execute("SELECT DISTINCT asset_in FROM buy");
assets=dbcursor.fetchall()
print("Remaining:")
for asset in assets:
    dbcursor.execute("SELECT SUM(amount_in) FROM buy where asset_in='"+ asset[0] +"'");
    bought = dbcursor.fetchall()[0][0]
    dbcursor.execute("SELECT SUM(amount_in) FROM sell where asset_in='"+ asset[0] +"'");
    sold = dbcursor.fetchall() [0][0]
    if sold == None:
        sold=0
    if asset[0] != "EUR":
            print(asset[0] + ": " + str(Decimal(bought)-Decimal(sold)))
            
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("1800x900+30+30") 
root.title("Bitpanda Tax Commander")


columns = ('tid_buy','tid_sell','date_buy','date_sell','asset','amount','amount_eur_buy','amount_eur_sell','date_diff','win')
transactiontable = ttk.Treeview(root, height=40, columns=columns, show='headings')
transactiontable.grid(row=0, column=0, sticky='news')
index=0
for col in columns:
    transactiontable.heading(col, text=col)
    if index == 0:
        transactiontable.column(col, width=250)
    elif index == 1:
        transactiontable.column(col, width=250)
    elif index == 4:
        transactiontable.column(col, width=50)
    else:
        transactiontable.column(col, width=130)
    index+=1
    
dbcursor.execute("SELECT * FROM transactions");
sumspend = dbcursor.fetchall()


for rec in sumspend:
        l1=list(rec)
        l1.append(rec[7]-rec[6])
        transactiontable.insert('', 'end', value=l1)

transactiontable.place(x=200,y=30)


columns = ('ASSET', 'AMOUNT_LEFT')
assettable = ttk.Treeview(root, height=40, columns=columns, show='headings')
assettable.grid(row=0, column=0, sticky='news')
assettable.heading(columns[0], text=columns[0])
assettable.column(columns[0], width=50)
assettable.heading(columns[1], text=columns[1])
assettable.column(columns[1], width=130)

dbcursor.execute("SELECT DISTINCT asset_in FROM buy");
assets=dbcursor.fetchall()
print("Remaining:")
for asset in assets:
    dbcursor.execute("SELECT SUM(amount_in) FROM buy where asset_in='"+ asset[0] +"'");
    bought = dbcursor.fetchall()[0][0]
    dbcursor.execute("SELECT SUM(amount_in) FROM sell where asset_in='"+ asset[0] +"'");
    sold = dbcursor.fetchall() [0][0]
    if sold == None:
        sold=0
    if asset[0] != "EUR":
            assettable.insert('', 'end', value=[asset[0],str(round(Decimal(Decimal(bought).normalize()-Decimal(sold).normalize()).normalize(),10).normalize())])
     
columns = ('tid_buy','tid_sell','date_buy','date_sell','asset','amount','amount_eur_buy','amount_eur_sell','date_diff','win')
taxtransactiontable = ttk.Treeview(root, height=40, columns=columns, show='headings')
taxtransactiontable.grid(row=0, column=0, sticky='news')
index=0
for col in columns:
    taxtransactiontable.heading(col, text=col)
    if index == 0:
        taxtransactiontable.column(col, width=250)
    elif index == 1:
        taxtransactiontable.column(col, width=250)
    elif index == 4:
        taxtransactiontable.column(col, width=50)
    else:
        taxtransactiontable.column(col, width=130)
    index+=1

assettable.place(x=3,y=10)
taxtransactiontable.place(x=200,y=30)

dbcursor.execute("SELECT * FROM transactions");
sumspend = dbcursor.fetchall()
y2015=0
y2016=0
y2017=0
y2018=0
y2019=0
y2020=0
y2021=0
y2022=0
y2023=0
y2024=0
y2025=0
print("Transaction less 1 year:")
for elem in sumspend:
    selldate=dateutil.parser.parse(elem[3])
    buydate=dateutil.parser.parse(elem[2])
    if selldate-buydate < timedelta(days=366):
        print(dateutil.parser.parse(elem[3])-dateutil.parser.parse(elem[2]))
        print(elem)
        l1=list(elem)
        l1.append(elem[7]-elem[6])
        taxtransactiontable.insert('', 'end', value=l1)
        if selldate.year==2025:
            y2025+=elem[7]-elem[6]
        elif selldate.year==2024:
            y2024+=elem[7]-elem[6]
        elif selldate.year==2023:
            y2023+=elem[7]-elem[6]
        elif selldate.year==2022:
            y2022+=elem[7]-elem[6]
        elif selldate.year==2021:
            y2021+=elem[7]-elem[6]
        elif selldate.year==2020:
            y2020+=elem[7]-elem[6]
        elif selldate.year==2019:
            y2019+=elem[7]-elem[6]
        elif selldate.year==2018:
            y2018+=elem[7]-elem[6]
        elif selldate.year==2017:
            y2017+=elem[7]-elem[6]
        elif selldate.year==2016:
            y2016+=elem[7]-elem[6]
        elif selldate.year==2015:
            y2015+=elem[7]-elem[6]

print("Year 2019: " + str(y2019))
print("Year 2020: " + str(y2020))
print("Year 2021: " + str(y2021))

columns = ('YEAR', 'EUR')
taxtable = ttk.Treeview(root, height=15, columns=columns, show='headings')
taxtable.grid(row=0, column=0, sticky='news')
taxtable.heading(columns[0], text=columns[0])
taxtable.column(columns[0], width=50)
taxtable.heading(columns[1], text=columns[1])
taxtable.column(columns[1], width=50)

taxtable.place(x=1690,y=30)
taxtable.insert('', 'end', value=["2015",str(round(y2015,2))])
taxtable.insert('', 'end', value=["2016",str(round(y2016,2))])
taxtable.insert('', 'end', value=["2017",str(round(y2017,2))])
taxtable.insert('', 'end', value=["2018",str(round(y2018,2))])
taxtable.insert('', 'end', value=["2019",str(round(y2019,2))])
taxtable.insert('', 'end', value=["2020",str(round(y2020,2))])
taxtable.insert('', 'end', value=["2021",str(round(y2021,2))])
taxtable.insert('', 'end', value=["2022",str(round(y2022,2))])
taxtable.insert('', 'end', value=["2023",str(round(y2023,2))])
taxtable.insert('', 'end', value=["2024",str(round(y2024,2))])
taxtable.insert('', 'end', value=["2025",str(round(y2025,2))])


columns = ('tid','date','asset_in','amount_in','amount_eur','transfer','deposit')
buytable = ttk.Treeview(root, height=40, columns=columns, show='headings')
buytable.grid(row=0, column=0, sticky='news')
index=0
for col in columns:
    buytable.heading(col, text=col)
    if index == 0:
        buytable.column(col, width=250)
    elif index == 1:
        buytable.column(col, width=250)
    elif index == 4:
        buytable.column(col, width=50)
    else:
        buytable.column(col, width=130)
    index+=1
    
dbcursor.execute("SELECT * FROM buy");
sumspend = dbcursor.fetchall()


for rec in sumspend:
        buytable.insert('', 'end', value=rec)

buytable.place(x=200,y=30)

columns = ('tid','date','asset_in','amount_in','amount_eur','withdraw')
selltable = ttk.Treeview(root, height=40, columns=columns, show='headings')
selltable.grid(row=0, column=0, sticky='news')
index=0
for col in columns:
    selltable.heading(col, text=col)
    if index == 0:
        selltable.column(col, width=250)
    elif index == 1:
        selltable.column(col, width=250)
    elif index == 4:
        selltable.column(col, width=50)
    else:
        selltable.column(col, width=130)
    index+=1
    
dbcursor.execute("SELECT * FROM sell");
sumspend = dbcursor.fetchall()


for rec in sumspend:
        selltable.insert('', 'end', value=rec)

selltable.place(x=200,y=30)



var = tk.StringVar()
label = ttk.Label( root, textvariable=var,font=('Helvetica', 12, 'bold'))

var.set("Tax Relevant Transactions (<1Y)")
label.place(x=200,y=5)

def BuyDetails():
   curItem = buytable.focus()
   print (buytable.item(curItem))
   itemdata=list([*buytable.item(curItem).values()])
   print(itemdata[2])
   detailswindow=tk.Tk()
   detailswindow.geometry("1800x900+30+30") 
   detailswindow.title(itemdata[2][0])
   columns = ('tid','date','asset_in','amount_in','amount_eur','transfer','deposit')
   detailbuy = ttk.Treeview(detailswindow, height=1, columns=columns, show='headings')
   detailbuy.grid(row=0, column=0, sticky='news')
   index=0
   for col in columns:
     detailbuy.heading(col, text=col)
     if index == 0:
        detailbuy.column(col, width=250)
     elif index == 1:
        detailbuy.column(col, width=250)
     elif index == 4:
        detailbuy.column(col, width=50)
     else:
        detailbuy.column(col, width=130)
     index+=1
   detailbuy.insert('', 'end', value=itemdata[2])
   print(itemdata[2][3])
   amountleft=Decimal(itemdata[2][3])
   dbcursor.execute("SELECT tid_sell,date_sell,asset,amount,amount_eur_sell FROM transactions WHERE tid_buy='"+ itemdata[2][0] + "'")
   sumspend = dbcursor.fetchall()
   columns = ('tid_sell','date','asset','amount','amount_eur_sell')
   detailbuy2 = ttk.Treeview(detailswindow, height=10, columns=columns, show='headings')
   detailbuy2.grid(row=0, column=0, sticky='news')
   index=0
   for col in columns:
     detailbuy2.heading(col, text=col)
     if index == 0:
        detailbuy2.column(col, width=250)
     elif index == 1:
        detailbuy2.column(col, width=250)
     elif index == 4:
        detailbuy2.column(col, width=50)
     else:
        detailbuy2.column(col, width=130)
     index+=1
   columns = ('tid_sell','date','asset','amount','amount_eur_sell')
   detailbuy3 = ttk.Treeview(detailswindow, height=1, columns=columns, show='headings')
   detailbuy3.grid(row=0, column=0, sticky='news')
   index=0
   for col in columns:
     detailbuy3.heading(col, text=col)
     if index == 0:
        detailbuy3.column(col, width=250)
     elif index == 1:
        detailbuy3.column(col, width=250)
     elif index == 4:
        detailbuy3.column(col, width=100)
     else:
        detailbuy3.column(col, width=130)
     index+=1
   for rec in sumspend:
         detailbuy2.insert('', 'end', value=rec)
         print(amountleft)
         print(rec[3])
         print(Decimal(str(rec[3])))
         amountleft -= Decimal(str(rec[3]))
   print(amountleft)      
   detailbuy2.place(x=0,y=50)
   detailbuy3.place(x=0,y=400)
   detailbuy3.insert('', 'end', value=[' ',' ','Left:',str(amountleft.normalize()),' '])

BuyDetails = ttk.Button(root, text ="Details", command = BuyDetails)

def helloCallBack():
   transactiontable.grid()
   transactiontable.grid_remove()
   taxtransactiontable.grid()
   taxtransactiontable.grid_remove()
   buytable.grid()
   buytable.grid_remove()
   selltable.grid()
   selltable.grid_remove()
   transactiontable.place(x=200,y=30)
   BuyDetails.grid()
   BuyDetails.grid_remove()
   var.set("All Transactions")

def taxCallback():
   transactiontable.grid()
   transactiontable.grid_remove()
   taxtransactiontable.grid()
   taxtransactiontable.grid_remove()
   buytable.grid()
   buytable.grid_remove()
   selltable.grid()
   selltable.grid_remove()
   taxtransactiontable.place(x=200,y=30)
   BuyDetails.grid()
   BuyDetails.grid_remove()
   var.set("Tax Relevant Transactions (<1Y)")
   
def enableBuyCallback():
   transactiontable.grid()
   transactiontable.grid_remove()
   taxtransactiontable.grid()
   taxtransactiontable.grid_remove()
   buytable.grid()
   buytable.grid_remove()
   selltable.grid()
   selltable.grid_remove()
   buytable.place(x=200,y=30)
   var.set("Crypto Buy Transactions")
   BuyDetails.place(x=1100,y=5)
   
def enablesellCallback():
   transactiontable.grid()
   transactiontable.grid_remove()
   taxtransactiontable.grid()
   taxtransactiontable.grid_remove()
   buytable.grid()
   buytable.grid_remove()
   selltable.grid()
   selltable.grid_remove()
   selltable.place(x=200,y=30)
   BuyDetails.grid()
   BuyDetails.grid_remove()
   var.set("Crypto Sell Transactions")

from tkinter import simpledialog

def DonateCallback():
   donatewindow=tk.Tk()
   donatewindow.geometry("800x200+30+30") 
   donatewindow.title("Donate")
   text = tk.Text(donatewindow,width=200, height=100)
   text.insert("1.0","This software is free for use and Opensource!\r\n")
   text.insert("1.0","If that application helped you and you wanna support further development with some coffee:\r\n")
   text.insert("2.0","BTC: bitcoin:bc1qtn4xm4krd70nr4k0nrlvcmwtqv93pqhgvge7d7\r\n")
   text.insert("3.0","BCH: bitcoincash:qzne8f2k6ltx3dh3g2jqgu64vjr4ge6mrufqk0fr3j\r\n")
   text.insert("4.0","ETH: ethereum:0xb35cF04E6F83C0baA79330bB166304D80F95Fb29\r\n")
   text.insert("5.0","ETC: ethclassic:0xE96f1f8038b4366AeF72EFe3B818958f372F99A4\r\n")
   text.insert("6.0","TRX: tron:TBr1f1NHoVc16WazKK22arh6MF54frRf88\r\n")
   text.insert("7.0","Doge: dogecoin:DBFkUcgZwAESzRHD1cNsior83JcQrgubtW\r\n")
   text.place(x=2,y=2)

   
transactiontable.grid()
transactiontable.grid_remove()
buytable.grid()
buytable.grid_remove()
selltable.grid()
selltable.grid_remove()

B = ttk.Button(root, text ="Transactions", command = helloCallBack)
B.place(x=1440,y=5)
B = ttk.Button(root, text ="Tax relevant Transactions", command = taxCallback)
B.place(x=1520,y=5)
B = ttk.Button(root, text ="Sell Transactions", command = enablesellCallback)
B.place(x=1340,y=5)
B = ttk.Button(root, text ="Buy Transactions", command = enableBuyCallback)
B.place(x=1240,y=5)
B = ttk.Button(root, text ="Donate", command = DonateCallback)
B.place(x=1700,y=5)
BuyDetails.grid_remove()
root.mainloop()