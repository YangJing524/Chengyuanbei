import json
import pickle
import demjson
import requests
import time
import math



def gcj2wgs(loc):

    lon = float(loc.split(',')[0])
    lat = float(loc.split(',')[1])
    a = 6378245.0
    ee = 0.00669342162296594323
    PI = 3.14159265358979324
    # convert way
    x = lon - 105.0
    y = lat - 35.0
    # longtitude
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    dLon += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLon += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    dLon += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    # lattitude
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    dLat += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLat += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    dLat += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI)
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return wgsLon, wgsLat


data=json.load(open('西城区格网坐标点.json','r',encoding='utf8'))
a=demjson.decode(data[0]['_jsonBounding'])

header={
        "Authorization": "",
        "X-Auth-Token": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "version": "Android 8.5.1",
        "deviceID": "",
        "Content-Type": "application/json",
        "Host": "lbs.amap.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

key = '27ff9958e48d17b03afa5cf06e9ae185'
url="https://restapi.amap.com/v3/traffic/status/rectangle?rectangle={0},{1};{2},{3}&extensions=all&key="+key
d={}
currentTime = time.ctime()
_length=len(a)
for i in range(_length):
    x_min=a[i]['x_min']
    y_min=a[i]['y_min']
    x_max=a[i]['x_max']
    y_max=a[i]['y_max']
    response=requests.get(url.format(x_min,y_min,x_max,y_max),headers=header)
    d[i]=response.content.decode('utf-8')
    d['Datetime']=currentTime
    time.sleep(round(1/18,3))

tmp=time.ctime()[:-5].split(':')

file_name=tmp[0]+'时'+tmp[1]+'分'+tmp[2]+'秒'

with open('{}.txt'.format(file_name),'wb') as f:
    pickle.dump(d,f)

# with open('dump.txt','rb+') as f:
#     pickle.load(f)