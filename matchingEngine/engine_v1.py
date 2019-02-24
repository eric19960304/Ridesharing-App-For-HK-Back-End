import redis
from sanic import Sanic
from sanic import response
from time import sleep, gmtime, strftime, time
import ujson
import requests

RIDE_REQUEST = 'realTimeRideRequest'
SEAT_NUM = 'seatNum'
DRIVER_LOCATION = 'driverLocation'

SERVER_ENDPOINT = 'http://localhost/notify-match-result/real-time-ride'

def getTimeStr():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def startEngine():
    # connect to redis
    try:
        redisConn = redis.StrictRedis(host='localhost', port=6379)
        print('Connected to redis')
    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

    print("[{}] wait for ride request".format( getTimeStr() ))
    while True:
        rideRequestJSONString = redisConn.lpop(RIDE_REQUEST)
        if rideRequestJSONString == None:
            # when there is no item in list, the result retunrned from redis is None
            sleep(3)
        else:
            rideRequest = ujson.loads( rideRequestJSONString.decode('utf-8') )
            run_match(rideRequest, redisConn)
            print("[{}] wait for ride request".format( getTimeStr() ))


def run_match(rideRequest, redisConn):
    driverLocationsDirty = redisConn.hgetall(DRIVER_LOCATION)
    
    print("[{}] wait for active driver".format( getTimeStr() ))

    if len(driverLocationsDirty) == 0:
        while True:
            # no driver yet, enter wait loop
            sleep(3)
            driverLocationsDirty = redisConn.hgetall(DRIVER_LOCATION)
            if len(driverLocationsDirty) > 0:
                # driver appears, exit wait loop
                break

    # clean up the data from redis
    driverLocations = dict()
    for (userIdDirty, locationDirty) in driverLocationsDirty.items():
        userId = userIdDirty.decode('utf-8')
        location = ujson.loads( locationDirty.decode('utf-8') )
        driverLocations[userId] = location

    # ready to start matching

    matchResult = find_one_match(rideRequest, list(driverLocations.items()))
    requests.post(url = SERVER_ENDPOINT, json = matchResult)


def find_one_match(rideRequest, driverLocationsList):
    '''
    rideRequest format:
    {
        userId: string,
        startLocation: {
            latitude: number,
            longitude: number
        },
        endLocation: {
            latitude: number,
            longitude: number
        }
        timestamp: number
    }

    driverLocationsList format list of tuple (string, dict):
    [
        (
            string,  <--- userId
            {
                "location":  {
                    "accuracy": number,
                    "altitude": number,
                    "altitudeAccuracy": number,
                    "heading": number,
                    "latitude": number,
                    "longitude": number,
                    "speed": number
                },
                "timestamp": number
            }
        ),
        ...
    ]
    '''
    print('rideRequest', rideRequest)
    print('userId', rideRequest['userId'])
    startlatitude = rideRequest['startLocation']['latitude']
    startlongitude = rideRequest['startLocation']['longitude']
    endlatitude = rideRequest['endLocation']['latitude']
    endlongitude = rideRequest['endLocation']['longitude']
    print('start location: lat=', startlatitude, 'long=', startlongitude)
    print('end location: lat=', endlatitude, 'long=', endlongitude)

    lastestDriverLocationIdx = None
    i = 0
    for _ in driverLocationsList:
        # get lastest location index
        if lastestDriverLocationIdx == None or driverLocationsList[i][1]['timestamp'] > driverLocationsList[lastestDriverLocationIdx][1]['timestamp']:
            lastestDriverLocationIdx = i
        i += 1

    

    matchResult = {
        "rider": rideRequest,
        "driver": {
            "userId": driverLocationsList[lastestDriverLocationIdx][0],
            "location": driverLocationsList[lastestDriverLocationIdx][1]['location'],
            "timestamp": driverLocationsList[lastestDriverLocationIdx][1]['timestamp']
        },
        "timestamp": time()
    }

    print('matchResult: ', matchResult)
    
    return matchResult


if __name__ == '__main__':
    startEngine()