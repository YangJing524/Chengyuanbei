import json
import demjson
import os
import requests
import re
import time
import arcpy
import numpy as np
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')
import math


data=json.load(open('西城区格网坐标点.json','r',encoding='utf8'))
a=demjson.decode(data[0]['_jsonBounding'])

header={
        "Authorization": "",
        "X-Auth-Token": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "version": "Android 8.5.1",
        "deviceID": "",
        "channelID": "PPZhuShou",
        "Content-Type": "application/json",
        "Host": "restapi.amap.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

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
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI);
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI);
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return wgsLon, wgsLat

def getShapefile():
    key = 'b01803a8d6382fc3dbeaf2d7fcf319df'
    # subdistrict=1 can set [0,1,2,3]


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
    def get_line():
        spRef = arcpy.SpatialReference("WGS 1984")
        name=districts_level['name']
        lines = districts_level['polyline'].split('|')
        featureList=[]
        for line in lines:
            points = line.split(";")
            point = arcpy.Point()
            array = arcpy.Array()
            for p in points:
                point.X, point.Y = gcj2wgs(p)
                array.add(point)
            polyline = arcpy.Polygon(array, spRef)
            featureList.append(polyline)

        arcpy.CopyFeatures_management(featureList, os.path.split(output_tabel_path)[0]+"\\"+city_param+'_'+name+'.shp')


    _length=len()
    x_min = a[0]['x_min']
    y_min = a[0]['y_min']
    x_max = a[0]['x_max']
    y_max = a[0]['y_max']

    url = "https://restapi.amap.com/v3/traffic/status/rectangle?rectangle={0},{1};{2},{3}&extensions=all&key=" + key
    _url = url.format(x_min, y_min, x_max, y_max)
    response = requests.get(_url, headers=header)

    get_line()

    arcpy.AddMessage("==Success to create shape file==")
    arcpy.AddMessage("==== Made by YangJing =====")
    time.sleep(3)
    # try:
    #     get_line()
    # except :
    #     arcpy.AddMessage("Can not create polyline" )
    #     pass

getShapefile()