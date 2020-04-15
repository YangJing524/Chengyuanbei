# coding:utf-8
# author: yangjing
# time:2020-01-08

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

province_param=arcpy.GetParameterAsText(0)
city_param=arcpy.GetParameterAsText(1)
categor_param=arcpy.GetParameterAsText(2)
output_tabel_path=arcpy.GetParameterAsText(3)

# province_param="北京市"
# city_param="北京市"
# categor_param="加油站"
# output_tabel_path=r"C:\Users\YJ\Desktop\城垣\基础数据库\POI_beijing.gdb"


out_Layer=os.path.join(output_tabel_path,categor_param)
saved_Layer = os.path.split(output_tabel_path)[0]+'\\'+ categor_param+ '_' +city_param + '.lyr'

if not arcpy.Exists(output_tabel_path):
    arcpy.AddMessage("the gdb file dose not exists")
    sys.exit(0)

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

def geocodeBaidu(address):
    address=re.sub('%s|中国%s'%(province_param,province_param),'',address)
    if len(re.findall('%s'%city_param,address))==2:
        address=re.sub('%s'%city_param,'',address,count=1)
    if len(address)>=17:
        address=address[: 17]+'...'
    base_url = "http://api.map.baidu.com/geocoder?address={address}&output=json&key=yXr0pGqmWbFMEapTD2bxg2D362dCVinl".format(address=address)

    response = requests.get(base_url)

    try:
        answer = response.json()
        latitude = answer['result']['location']['lat']
        longitude = answer['result']['location']['lng']
        # time.sleep(1)
        return longitude,latitude
    except :
        arcpy.AddMessage('No response in BaiduMap :%s'%response.status_code)
        return '',''


def geocodeGaode(address):
    key='b01803a8d6382fc3dbeaf2d7fcf319df'
    base_url = "https://restapi.amap.com/v3/place/text?keywords={}&city={}&offset=20&page=1&key={}&extensions=base".format(address,city_param,key)
    response = requests.get(base_url,headers=header)
    try:
        answer = response.json()
        # locat = answer['pois'][0]['location']
        # latitude=locat.split(',')[1]
        # longitude = locat.split(',')[0]
        # # tel=answer['pois'][0]['tel']
        # # time.sleep(1)s
        # return longitude, latitude

        return answer['pois'][0]
    except:
        arcpy.AddMessage(response.status_code)
        return '', ''


def getGaodePois(keyword):

    key = 'b01803a8d6382fc3dbeaf2d7fcf319df'
    # Eight locations
    city_code=["110101","110102","110105","110106","110107","110108"]



    url1 = "https://restapi.amap.com/v3/place/text?keywords="+keyword+"&city="
    url2 = "&output=JSON&offset=45&key=b01803a8d6382fc3dbeaf2d7fcf319df&extensions=all&page="
    x = []
    col=['name','type','address','adname','long','lat']
    num = 0
    for i in range(0, len(city_code)):
        city = city_code[i]
		# set the max deep of page is 80  optional:1~100
        for page in range(1, 80):
            # if page == 45:
            #     pass
            thisUrl = url1 + city + url2 + str(page)
            data = requests.get(thisUrl)
            s = data.json()
            aa = s["pois"]
            if len(aa) == 0:
                break
            for k in range(0, len(aa)):
                s1 = aa[k]["name"]
                s2 = aa[k]["type"]
                s3 = aa[k]["address"]
                # to avoid the ValueError: setting an array element with a sequence.
                if isinstance(s3,list):
                    s3=' '
                s4 = aa[k]["adname"]
                long,lat = gcj2wgs(aa[k]["location"])
                # to avoid ValueError: setting an array element with a sequence
                x.append([s1, s2, s3, s4, float(long), float(lat)])

                num += 1
                arcpy.AddMessage("Crawl " + str(num) + " pieces of data")
            time.sleep(1)

    arcpy.AddMessage("==Success crawl data from internet==")
    arcpy.AddMessage("=======Made by YangJing==========")
    # c = pd.DataFrame(x) #unable to install pandas
    # try:
    #     c.to_excel(keyword+r'.xlsx', index = False,columns=col)
    # except:
    #     c.to_csv(keyword+'.csv', encoding='utf-8-sig',index = False,columns=col)

    arr=np.array(x)
    # np.save('01.npy',arr)
    arcpy.AddMessage("...Store data to csv...")
    #
    struct_array = np.core.records.fromarrays(arr.transpose(), np.dtype(
        [('name', 'U50'), ('type', 'U50'), ('address', 'U150'), ('adname', 'U50'), ('long', '<f8'), ('lat', '<f8')]))
    try:
        arcpy.da.NumPyArrayToTable(struct_array, output_tabel_path+'\\'+categor_param+ '_' +city_param)
    except:
        arcpy.Delete_management(output_tabel_path+'\\'+categor_param+ '_' +city_param)
        arcpy.da.NumPyArrayToTable(struct_array, output_tabel_path + '\\' + categor_param + '_' +city_param)


    arcpy.AddMessage("The data has stored in "+output_tabel_path+'\\'+categor_param)
    arcpy.AddMessage("==================================")

    arcpy.AddMessage("Display xy data")
    spRef=arcpy.SpatialReference("WGS 1984")
	# xy transform to point
    arcpy.MakeXYEventLayer_management(output_tabel_path+'\\'+categor_param+ '_' +city_param, "long", "lat", out_Layer, spRef)
    arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)


def getShapefile():
    key = 'b01803a8d6382fc3dbeaf2d7fcf319df'
    # subdistrict=1 can set [0,1,2,3]
    url = "http://restapi.amap.com/v3/config/district?extensions=all&subdistrict=0&key=" + key

    city_code = ["110100","110101", "110102", "110105", "110106", "110107", "110108"]
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


getGaodePois(categor_param)
# getShapefile()
