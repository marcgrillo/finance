import datetime
import http.client, urllib.request, urllib.parse, urllib.error, base64, re
import numpy as np
import time


#circa 0.3 secondi a riga
righe=2016000

def history(a):
    
    body = a[2:-4]
    closeprice = []

    for key in body:
       if "Close" in key:
           c = key.split(':')
           close = float(re.findall('\d+\.\d+', c[1] )[0])
           closeprice.append(close) 

    return closeprice
    

def updatebit():
    
    conn = http.client.HTTPSConnection('candle.etoro.com')
    # 480 is 480 periods of 1 hour, 100000 is Bitcoin
    conn.request("GET", "/candles/asc.json/OneMinute/1/100000")
    response = conn.getresponse()
    data = response.read()
    data=data.decode("utf-8")
    a = data.split(',')
    closeprice = history(a)

    
    return closeprice[0]
    
    
 
for j in range(righe):
    file1 = open("varianze_bitcoin.txt", "a")  # append mode
    file1.write(str(datetime.datetime.now())+','+str(updatebit())+'\n')
    file1.close()