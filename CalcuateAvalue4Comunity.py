# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 10:09:47 2021

@author: b1081921
"""

import sys, os 
import uuid
cellsize=40
import math
import arcpy
from arcpy import env
import pandas as pd
import requests
import json
arcpy.CheckOutExtension("3D")
import numpy as np
import pandas as pd
from urllib.request import urlopen
import csv
root=r'C:\CQHousePrice\肉'
appliedRoot= r'C:\CQHousePrice\CQFood_result.gdb\Foodclass'
in_onept_shp ="oneCommunityPts.shp"
outAvalue=0
community_pts_shp =os.path.join(root, "commounties_price_meats.shp")
veg_pts_shp = os.path.join(appliedRoot, "meats_CC") #Fruit vegetable Griant milk seafood meats egg
arcpy.MakeFeatureLayer_management(veg_pts_shp,"veg_pts_shp_lyr")
arcpy.MakeFeatureLayer_management(community_pts_shp,"community_pts_shp_lyr")
communitybufoutput = os.path.join(root, "buff4pt.shp")
vegbufoutput = os.path.join(root, "vegbuff4pt.shp")
SelectVegsPts = os.path.join(root, "SelectVegsPts.shp")
SelectCommuPts = os.path.join(root, "SelectCommuPts.shp")
badu_AK = ['LVeetS51WxCkcvk8W1ZtH2M6M3sAcd7B','vyWV1Nir0wfARSkzkPOONYfrmQg8Lhlc','vyWV1Nir0wfARSkzkPOONYfrmQg8Lhlc','ubxeG6bwLXvViIxvtk3q1lRlBV5hvGVi','WIoulempg3Tj8UYzbTAIDFbqXyZbZgo3','DKQMQtBSORoTT57U5Dt6VPP176hDGmFH','qtvRqX6N2as61vgjuMtqXnGBshq9SqX0','ETpsECGpVj23QTTWY2fDEHAcnk2koeDh','hP44FFQHCbhbFPWN1KQjIyNfsppsbPSA','3qajGwXQIVSIzfDg6LBD7imGPQnZYNiY']
comunity2poiDic={}

#print(' 当前时间：'+ time.localtime(time.time()))

with open('matrixTimespend_meats.csv',encoding="utf-8") as f:#matrixTimespendFruits
    reader = csv.reader(f)
    header_row = next(reader)
    comunity2poiDic[header_row[0]]=int(header_row[1])
    datas = []
    for row in reader:
        if(len(row)>0):
            k1=row[0]
            if comunity2poiDic.__contains__(row[0])==False: # 减少服务器的访问省钱  
                comunity2poiDic[k1]= int(row[1])
#comunity2poiDic={}
# 定义生成一个点的函数
def generate_one_point_featureclass(strx,stry,spatialref):
# for row in arcpy.da.SearchCursor(Onepoint_shp, ["SHAPE@XY"]):
# stry=2960066.898#'2961233'#2961245.48395      
    x =float(strx)
    y =float(stry)
    point = arcpy.Point(x, y)
    ptGeometry = arcpy.PointGeometry(point,spatialref)
    
    if arcpy.Exists(in_onept_shp):
        arcpy.Delete_management(in_onept_shp)
    arcpy.CopyFeatures_management(ptGeometry, in_onept_shp)    
pass
def call_matrix_api(origins, destinations):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    key = 'AIzaSyD77ir55dLoCVmLlszWz3XpQKp-XI-Uh1Y'  # INSERT API KEY !!!
    params = {'key': key, 'origins': origins, 'destinations': destinations,'mode':'walking'} #'mode':'walking' DRIVING BICYCLING TRANSIT

    req = requests.get(url=url, params=params)
    api_response = json.loads(req.content)    
    return api_response
pass

def call_matrix_baidu_api(origins, destinations,ak):
    out_lat = str(origins).split(',')[0]
    out_lng = str(origins).split(',')[1]
    des_lat = str(destinations).split(',')[0]
    des_lng = str(destinations).split(',')[1]
    url_drive = r"http://api.map.baidu.com/routematrix/v2/walking?output=json&origins={0},{1}&destinations={2},{3}&{4}&tactics=11&coord_type={4}&ak={5}".format(out_lat,out_lng,des_lat,des_lng,'wgs84',ak)
    url_drive = url_drive.replace(" ","")
    
    
    while True:
        try:
            result_drive = json.loads(urlopen(url_drive).read())  # json转dict
            break
        except:
            print(url_drive)
            return '失败'
#            tracebake.print_exc()    
    return result_drive
pass

def get_G(x):
    if x < 1200:
        G=(np.exp(-0.5*(x/1200)**2)-np.exp(-0.5))/(1-np.exp(-0.5))
        return G
    else:
        return 0
pass
def get_RJ(sj,timelist):
    for i in range(len(timelist)):
        v1= sj*get_G(timelist[i])
    return v1
pass

spatial_ref=arcpy.SpatialReference(4326) 
Coordinate_System = arcpy.SpatialReference(4326) 
arcpy.env.workspace = root
arcpy.env.overwriteOutput = True
feature_classes = arcpy.ListFeatureClasses()
for fc in feature_classes:
    spatial_ref = arcpy.Describe(fc).spatialReference
    if spatial_ref.name == "Unknown":
        print("{0} has an unknown spatial reference".format(fc))
    else:
        print("{0} : {1}".format(fc, spatial_ref.name))
        break

if arcpy.Exists('community_pts_shp_lyr'):
    arcpy.Delete_management('community_pts_shp_lyr')
arcpy.MakeFeatureLayer_management(community_pts_shp, 'community_pts_shp_lyr')

# =============================================================================
# Thiessen_shp_select = "Thiessen_shp_select.shp"                     
# if arcpy.Exists(Thiessen_shp_select):
#     arcpy.Delete_management(Thiessen_shp_select)
# =============================================================================
# fields = ["UID","xh","SHAPE@AREA"]
# fieldList=arcpy.ListFields(community_pts_shp)
# field_name_List=[]
# for field in fieldList:
#     field_name_List.append(field.name)
# if 'Shape_Area' not in field_name_List:
#     arcpy.AddField_management(community_pts_shp,'Shape_Area','DOUBLE',"#", "#", "#", "#","NON_NULLABLE", "NON_REQUIRED", "#")
#     arcpy.CalculateField_management(community_pts_shp,'Shape_Area','!shape.area!','PYTHON')

####第一步
fieldList=arcpy.ListFields(veg_pts_shp)
field_name_List=[]
for field in fieldList:
    field_name_List.append(field.name)
#if 'Rj' not in field_name_List:
#    arcpy.AddField_management(community_pts_shp,'Rj','DOUBLE',"#", "#", "#", "#","NON_NULLABLE", "NON_REQUIRED", "#")
fields =['TureID','SJ','RJ', 'SHAPE@XY']
akn =0
ak =badu_AK[akn]
with arcpy.da.UpdateCursor(veg_pts_shp,fields) as cursor_r:
    for prow in cursor_r:        
        pt= str(prow[3])[1:-1]
        dist=pt.split(',')[1]+','+ pt.split(',')[0]        
        Sj=prow[1]           
        poiid = prow[0]
# =============================================================================
#         if poiid <6000000:
#             continue
# =============================================================================
        generate_one_point_featureclass(pt.split(',')[0],pt.split(',')[1],spatial_ref)
        if arcpy.Exists(vegbufoutput):
            arcpy.Delete_management(vegbufoutput)
        arcpy.Buffer_analysis(in_onept_shp, vegbufoutput, "1350 Meters", "FULL", "ROUND", "NONE")
        arcpy.management.SelectLayerByLocation("community_pts_shp_lyr", "INTERSECT",vegbufoutput, None, "NEW_SELECTION", "NOT_INVERT")
        ListRjs=[]
        arcpy.CopyFeatures_management("community_pts_shp_lyr", SelectCommuPts)
        with arcpy.da.SearchCursor(SelectCommuPts, ['TureID','poup', 'SHAPE@XY']) as cursor3:
            for row4 in cursor3:
                communtityid = row4[0]
                key = str(communtityid)+'_'+ str(poiid)
                orginpt= str(row4[2])[1:-1]
                orgin=orginpt.split(',')[1]+','+ orginpt.split(',')[0]              
                poup = row4[1]
                if comunity2poiDic.__contains__(key)==False: # 减少服务器的访问省钱                   
                    result_drive = call_matrix_baidu_api(orgin,dist,ak)
                    if result_drive=='失败':
                        continue
                    status_drive = result_drive['status']
                    if status_drive == 0:  # 状态码为0：无异常
                        distance_drive = result_drive['result'][0]['distance']['value']  # 里程(米)
                        timesec_drive = result_drive['result'][0]['duration']['value']  # 耗时(秒)
                        comunity2poiDic[key]= timesec_drive    
                        if(timesec_drive<=1200):
                            ListRjs.append((timesec_drive,poup))
                        print(timesec_drive)
                    elif status_drive == 302 or status_drive == 210 or status_drive == 201:  # 302:额度不足;210:IP验证未通过                
                        akn += 1
                        ak = badu_AK[akn]
                        print('akn：'+str(akn))
                        result_drive = call_matrix_baidu_api(orgin,dist,ak)
                        if status_drive == 0:  # 状态码为0：无异常
                            distance_drive = result_drive['result'][0]['distance']['value']  # 里程(米)
                            timesec_drive = result_drive['result'][0]['duration']['value']  # 耗时(秒)
                            if comunity2poiDic.__contains__(key)==False: # 减少服务器的访问省钱
                                comunity2poiDic[key]= timesec_drive
                            if(timesec_drive<=1200):
                                ListRjs.append((timesec_drive,poup))
                    else:
                        print('请求错误')
                        #distance_drive = timesec_drive = '请求错误'
                else:
                    timesec_drive=comunity2poiDic[key]
                    if(timesec_drive<=1200):
                        ListRjs.append((timesec_drive,poup))     
        print('ID"'+str(prow[0])) 
        prow[2]=0              
        if len(ListRjs)>0:          
            Listarr = np.array(ListRjs)
            timearr = Listarr[:,0]
            pouparr= Listarr[:,1]
            sumjs=0
            for i in range(len(timearr)):
                sumjs=sumjs+ get_G(timearr[i])*pouparr[i]             
            if sumjs>0:
                prow[2]=Sj/sumjs                
                print(Sj/sumjs)
        else:            
            print(prow[0])
        cursor_r.updateRow(prow)

with open('matrixTimespend_meats2.csv','w') as f:
    w = csv.writer(f)
    w.writerows(comunity2poiDic.items())

####### 第二步
VKList=[]
fields2 =['TureID','price','poup','price','AI', 'SHAPE@XY']
with arcpy.da.UpdateCursor(community_pts_shp,fields2) as   cursor:
    for prow in cursor:
        #klist.append(prow.getValue('FID'))
        price=prow[1]
        poupulation=prow[2]
        price=prow[3]
        communtityid = prow[0]
        
        pt= str(prow[5])[1:-1]
        origin=pt.split(',')[1]+','+ pt.split(',')[0] 
    #    feat = prow.getValue[5]    
    #    y= feat.getPart().Y #prow.getValue('shape@X')
    #    x = feat.getPart().X        
        generate_one_point_featureclass(pt.split(',')[0],pt.split(',')[1],spatial_ref)
        
        #arcpy.CopyFeatures_management("veg__shp_lyr", veg_pts_shp)
        matchPtsncount = int(arcpy.GetCount_management('veg_pts_shp_lyr').getOutput(0))
        #测试建立空矩阵，默认值为5小时 1200 s
        listA=[]
        distance=[]
    #    with arcpy.da.SearchCursor(veg_pts_shp, ['FID', 'SHAPE@XY']) as cursor3:
    #        for row3 in cursor3:
    #            listdemand.append(row3[0])
    #            listA.append((row3[0], 12000,9999999))   
                
        if arcpy.Exists(communitybufoutput):
            arcpy.Delete_management(communitybufoutput)
        arcpy.Buffer_analysis(in_onept_shp, communitybufoutput, "1350 Meters", "FULL", "ROUND", "NONE")
        arcpy.management.SelectLayerByLocation("veg_pts_shp_lyr", "INTERSECT",communitybufoutput, None, "NEW_SELECTION", "NOT_INVERT")
          
        if arcpy.Exists(SelectVegsPts):
            arcpy.Delete_management(SelectVegsPts)
        arcpy.CopyFeatures_management("veg_pts_shp_lyr", SelectVegsPts)
        with arcpy.da.SearchCursor(SelectVegsPts, ['TureID','RJ', 'SHAPE@XY']) as cursor2: # must use fixed fieldname
            for row2 in cursor2:
                #print('Feature {} has an area of {}'.format(row2[0], row2[1]))                
                diststr= str(row2[2])[1:-1]
                dist=diststr.split(',')[1]+','+ diststr.split(',')[0]
                poiid = row2[0]
                distances=-1
                times=-1
                pRj = row2[1]
                key = str(communtityid)+'_'+ str(poiid)
                if comunity2poiDic.__contains__(key)==False: # 减少服务器的访问省钱  
                    api_response=call_matrix_api(origin,dist)                  
                    comunity2poiDic[key]= timesec_drive
                    
                    if api_response['status'] == 'OK':
                        for row in api_response['rows']:
                            for element in row['elements']:
                                if element['status'] == 'OK':
                                    distance =element['distance']['value']
                                    timesec_drive=element['duration']['value']
                                    if(timesec_drive<=1200):
                                        a=get_G(timesec_drive)*pRj                            
                                        listA.append(a)
                else:
                    timesec_drive=comunity2poiDic[key]    
                    if(timesec_drive<=1200):
                        a=get_G(timesec_drive)*pRj                            
                        listA.append(a)
        print('ID"'+str(prow[0])+'Len:'+str(len(listA)))   
        prow[4] = 0                             
        if len(listA)>0:  
            arr = np.array(listA)
            Aj= np.sum(arr)
            prow[4] = Aj
            
            print(Aj)
        else:
            prow[4] = 0
        cursor.updateRow(prow)


#

