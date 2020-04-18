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



'''
{'info': 'OK',
'infocode': '10000',
'status': '1',
'trafficinfo': {'description': '西局东街：西三环南路附近双向畅通。',
'evaluation': {'blocked': '0.00%',
'congested': '0.00%',
'description': '整体畅通',
'expedite': '100.00%',
'status': '1',
'unknown': '0.00%'},
'roads': [{'angle': '2',
'direction': '从西三环南路辅路到北京西站南路',
'lcodes': '7954,7955',
'name': '西局东街',
'polyline': '116.311913,39.8748627;116.313171,39.8748627;116.313408,39.8748703;116.315331,39.8748665;116.31601,39.8748703;116.316269,39.8748741;116.316376,39.8748894;116.316696,39.8749352;116.316833,39.8749542;116.31694,39.8749771;116.317284,39.8750648;116.31739,39.8750916;116.317467,39.8751183;116.317543,39.8751411;116.317627,39.8751564;116.31797,39.8751717;116.318634,39.8751717;116.319412,39.8751602;116.319771,39.8751717;116.319885,39.8751678;116.320038,39.8751717;116.320808,39.8751602;116.320961,39.8751602;116.321075,39.8751564',
'speed': '20',
'status': '1'},
{'angle': '183',
'direction': '从太平桥路到西三环南路辅路',
'lcodes': '-7953',
'name': '西局东街',
'polyline': '116.317963,39.875206;116.317619,39.8751831;116.317535,39.8751717;116.317459,39.875145;116.317368,39.8751183;116.317284,39.8750916;116.316933,39.8750076;116.316818,39.8749886;116.316673,39.8749619;116.316376,39.8749161;116.316269,39.8749008;116.31601,39.874897;116.315331,39.874897;116.313408,39.874897;116.313171,39.8748932;116.311913,39.8748932',
'speed': '20',
'status': '1'}]}}
'''



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


key = ['27ff9958e48d17b03afa5cf06e9ae185',
       '35dc4d625c8f5b84664b539f4c401dfe',
       'da0d3354c56524855a593987ea0b92a8',
       '703bad79f66eca19753ef0cf50ea27b3',
       'b987a8e0b64066946ec2ecffd8058d6d',
       '7b72177ac4bb0343cee4752393237215',
       'acb3533c2ef86be19384965e269868a4',
       '3118c58ea0560fe4052eb10c8c45a9eb',
       '8a10b13049fdf288efd116fba637ec7a',
       'b01803a8d6382fc3dbeaf2d7fcf319df'
       ]

data = json.load(open('西城区格网坐标点.json','r',encoding='utf8'))
a = demjson.decode(data[0]['_jsonBounding'])
url = "https://restapi.amap.com/v3/traffic/status/rectangle?rectangle={0},{1};{2},{3}&extensions=all&key="+key[0]
d = {}
currentTime = time.ctime()
_length = len(a)
for i in range(_length):
    x_min=a[i]['x_min']
    y_min=a[i]['y_min']
    x_max=a[i]['x_max']
    y_max=a[i]['y_max']
    response = requests.get(url.format(x_min,y_min,x_max,y_max),headers=header)
    d[i]=response.content.decode('utf-8')
    d['Datetime']=currentTime
    d['Weather']='多云 12~23C'
    time.sleep(round(1/18,3))

tmp=time.ctime()[:-5].split(':')

file_name=tmp[0]+'时'+tmp[1]+'分'+tmp[2]+'秒'

with open('{}.txt'.format(file_name),'wb') as f:
    pickle.dump(d,f)

# with open('dump.txt','rb+') as f:
#     pickle.load(f)



