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
        "User-Agent": "com.tianyancha.skyeye/Dalvik/2.1.0 (Linux; U; Android 9; oppo qbs Build/PKQ1.180819.001;)",
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

    x_min=a[0]['x_min']
    y_min=a[0]['y_min']
    x_max=a[0]['x_max']
    y_max=a[0]['y_max']

    url="https://restapi.amap.com/v3/traffic/status/rectangle?rectangle={0},{1};{2},{3}&extensions=all&key="+key
    url=url.format(x_min,y_min,x_max,y_max)

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

    # http://restapi.amap.com/v3/config/district?extensions=all&subdistrict=0&key=b01803a8d6382fc3dbeaf2d7fcf319df&keywords=110103
    for adcode in city_code:
        _url = url + "&keywords=" + adcode
        response = requests.get(_url, headers=header)
        try:
            districts_level = response.json()['districts'][0]
        except:
            districts_level = response.json()
        # districts_level = shapes['districts']
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