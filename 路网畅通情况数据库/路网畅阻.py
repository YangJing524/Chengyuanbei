# -*- coding: utf-8 -*-
import json
import pickle
import io
import demjson
import requests
import time
import numpy as np
import math
import arcpy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def gcj2wgs(loc):
    try:
        lon = float(loc.split(',')[0])
        lat = float(loc.split(',')[1])
    except IndexError as e:
        print loc
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


def creatTable(roadData):
    # with open('{}.txt'.format(file_name),'rb+') as f:
    #     roadData = pickle.load(f)

    _length = len(roadData)
    # featureList = []
    DATA=[]
    for i in range(_length):
        dict_data=json.loads(roadData[i])
        if dict_data['info'] == 'OK':
            def get_line():
                # Attribute

                try:
                    roadName = dict_data['trafficinfo']['roads'][0]['name']
                    description = dict_data['trafficinfo']['description']
                    block = dict_data['trafficinfo']['evaluation']['blocked']
                    congested = dict_data['trafficinfo']['evaluation']['congested']

                    expedite = dict_data['trafficinfo']['evaluation']['expedite']
                    polyline = dict_data['trafficinfo']['roads'][0]['polyline']
                    if roadName and description and polyline:DATA.append([roadName,description,block,congested,expedite,polyline])
                except Exception as e:
                    # arcpy.AddMessage(e)
                    return None
                # spRef = arcpy.SpatialReference("WGS 1984")
                # for points in polyline.split(';'):
                #     point = arcpy.Point()
                #     array = arcpy.Array()
                #     point.X, point.Y = gcj2wgs(points)
                #     array.add(point)
                #
                # polyline = arcpy.Polyline(array, spRef)
                # struct_array = np.core.records.fromarrays(arr.transpose(), np.dtype(
                #     [('name', 'U50'), ('type', 'U50'), ('address', 'U150'), ('adname', 'U50'), ('long', '<f8'),
                #      ('lat', '<f8')]))

                # arcpy.AddField_management(polyline, "roadName", "TEXT")
                # arcpy.AddField_management(polyline, "description", "TEXT")
                # arcpy.AddField_management(polyline, "block", "TEXT")
                # arcpy.AddField_management(polyline, "congested", "TEXT")
                # arcpy.AddField_management(polyline, "expedite", "TEXT")
                #
                # arcpy.CalculateField_management(polyline, 'roadName', str(roadName), "PYTHON_9.3")
                # arcpy.CalculateField_management(polyline, "description", str(description), "PYTHON_9.3")
                # arcpy.CalculateField_management(polyline, "block", block, "PYTHON_9.3")
                # arcpy.CalculateField_management(polyline, "congested", congested, "PYTHON_9.3")
                # arcpy.CalculateField_management(polyline, "expedite", expedite, "PYTHON_9.3")
                return polyline
            get_line()
            # if line: featureList.append(line)

        else:
            print('parse error')
            pass
    arr=np.array(DATA)
    struct_array = np.core.records.fromarrays(arr.transpose(), np.dtype(
        [('roadName', 'U50'), ('description', 'U150'), ('block', 'U15'), ('congested', 'U15'), ('expedite', 'U15'),('polyline', 'U150')]))

    name=file_name.replace(' ','_')
    try:
        arcpy.da.NumPyArrayToTable(struct_array, gdb_file + '\\' + name)
    except Exception as e:
        arcpy.AddMessage(e)


    # arcpy.CopyFeatures_management(featureList, file_name + '.shp')

    arcpy.AddMessage("==Success to create ROAD shapeFile==")
    arcpy.AddMessage("==== Made by YangJing =====")



def getRawJsonFile(file_name):
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
    f='西城区格网坐标点.json'.decode("utf-8")
    # right answer
    data = json.load(io.open(f,'r',encoding='utf8'))
    #
    a = demjson.decode(data[0]['_jsonBounding'])
    url = "https://restapi.amap.com/v3/traffic/status/rectangle?rectangle={0},{1};{2},{3}&extensions=all&key="+key[5]
    d = {}
    # currentTime = time.ctime()
    _length = len(a)
    for i in range(_length):
        x_min=a[i]['x_min']
        y_min=a[i]['y_min']
        x_max=a[i]['x_max']
        y_max=a[i]['y_max']
        response = requests.get(url.format(x_min,y_min,x_max,y_max),headers=header)
        d[i]=response.content.decode('utf-8')
        time.sleep(round(1 / 18, 3))
    # d['Datetime']=currentTime
    # d['Weather']='多云 12~23C'
    # creatline() function

    with open(unicode('{}.txt'.format(file_name),'utf-8'),'wb') as f:
        pickle.dump(d,f)
    arcpy.AddMessage('Success to save data')





if __name__=='__main__':
    tmp = time.ctime()[:-5].split(':')
    file_name = tmp[0] + '时' + tmp[1] + '分' + tmp[2] + '秒'
    print (file_name)
    # right-answer
    # open(unicode('{}.txt'.format(file_name),'utf-8'), 'wb')
    # getRawJsonFile(file_name)
    # file_name='Sat Apr 18 18时53分15秒'
    gdb_file=r'C:\Users\yj\Desktop\城 · 垣\路网畅通情况数据库\实时路网畅阻情况数据.gdb'
    file_name='Sat Apr 18 23时03分41秒'
    with open(unicode('{}.txt'.format(file_name),'utf-8'),'rb+') as f:
        roadData = pickle.load(f)
        creatTable(roadData)
