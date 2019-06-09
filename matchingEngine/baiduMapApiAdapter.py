
import os
import ujson
from loc import loc

from urllib.request import urlopen
import json
import numpy as np

ak=os.environ['BAIDU_MAP_API_KEY']

def getDistance(origin, destination, getDuration=False):
    '''
    Format of origin and destination:
    { "latitude": int, "longitude": int }

    Return the distance/duration pair from a origin to a destination
    return (distance in m : int, duration in seconds : int)
    '''
	# 利用百度地图计算两点之间的距离，因为谷歌在国内不好用。
    origin_url = 'http://api.map.baidu.com/direction/v2/driving?origin='
    origin_lat = origin['latitude']
    origin_lng = origin['longitude']
    dest_str = '&destination='
    dest_lat = destination['latitude']
    dest_lng = destination['longitude']
    ak_str = '&ak='+ak
	
	# 拼接字符串，然后向百度地图服务器发送请求
    url = origin_url + str(origin_lat)+','+str(origin_lng)+dest_str+str(dest_lat)+','+str(dest_lng)+ak_str
    response = urlopen(url)
    res_json = json.loads(response.read())
    duration_or_distance = 'distance'
    if(getDuration):
        duration_or_distance = 'duration'

    return res_json['result']['routes'][0][duration_or_distance]

def getDistanceMatrix(origins, destinations, getDuration=False):
    '''
    Format of origins and destinations:
    [ { "latitude": int, "longitude": int } ]

    Return the distance matrix as 2D list
    return [ [ (distance in m : int, duration in seconds : int) ] ]
    # e.g. origins = [A, B], destinations = [C, D, E]
    # return:
    # [ [ A->C, A->D, A->E ],
    #   [ B->C, B->D, B->E ] ] where A->C means the distance/duration tuple from point A to point C
    '''
    matrixSize = len(origins)*len(destinations)
    if(matrixSize>81):
        raise Exception('matrix size='+ str(matrixSize) +' exceeds the limit (we don\' have enough credit in Google Cloud!')
    origins_cord = ''
    i=0
    for loc in origins:
        if i == len(origins)-1:
            origins_cord += str(loc['latitude']) + ',' + str(loc['longitude'])
            break;
        origins_cord +=str(loc['latitude'])+','+str(loc['longitude'])+'|'
        i+=1

    # 把destination的坐标变成百度API要求的那个样子
    dest_cord = ''
    i = 0
    for loc in destinations:
        if i == len(destinations) - 1:
            dest_cord += str(loc['latitude']) + ',' + str(loc['longitude'])
            break;
        dest_cord += str(loc['latitude']) + ',' + str(loc['longitude']) + '|'
        i += 1

    origin_url = 'http://api.map.baidu.com/routematrix/v2/driving?output=json&origins='
    dest_str = '&destinations='
    ak_str = '&ak='+ak

    url = origin_url+origins_cord+dest_str+dest_cord+ak_str
    response = urlopen(url)
    res_json = json.loads(response.read())

    duration_or_distance = 'distance'
    if(getDuration):
        duration_or_distance = 'duration'
    result_matrix =[]
    result_list = []
    i = 0
    dests_len = len(destinations)
    for dist_dura in res_json['result']:

        result_list.append(dist_dura[duration_or_distance]['value'])
        i+=1
        if i%dests_len == 0:
            result_matrix.append(result_list)
            result_list = []
    return result_matrix

def getDistanceTest():
    print(getDistance(loc['hku'], loc['hku']))

def getDistanceMatrixTest():
    origins = [loc['hku'], loc['cu'], loc['ust']]
    # destinations = [ loc['ust'], loc['polyu'], loc['cityu'] ]
    destinations = origins
    matrix = getDistanceMatrix(origins, destinations)
    print(matrix)

if __name__ == "__main__":
    print('Test all methods:')
    getDistanceTest()
    # getDistanceMatrixTest()
    print('Tests passed.')

