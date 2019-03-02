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

    while True:
        
        queueLen = redisConn.llen(RIDE_REQUEST)
        onlineDriverCount =   redisConn.hlen(DRIVER_LOCATION)

        if queueLen > 0 and onlineDriverCount > 0:
            # consume one request from queue
            rideRequestJSONString = redisConn.lpop(RIDE_REQUEST)
            rideRequest = ujson.loads( rideRequestJSONString.decode('utf-8') )

            # get all driver locations
            driverLocationsRaw = redisConn.hgetall(DRIVER_LOCATION)
            driverLocations = dict()
            for (userIdDirty, locationDirty) in driverLocationsRaw.items():
                userId = userIdDirty.decode('utf-8')
                location = ujson.loads( locationDirty.decode('utf-8') )

                if( isDriverOnline(location) ):
                    driverLocations[userId] = location
                else:
                    # the driver is currently offline, delete his/her location
                    redisConn.hdel(DRIVER_LOCATION, userId)

            # ready to start matching
            matchResult = find_one_match(rideRequest, list(driverLocations.items()))
            requests.post(url = SERVER_ENDPOINT, json = matchResult)
        else:
            sleep(3)

def isDriverOnline(driverLocation):
    print('location time: ', driverLocation[1]['timestamp'])
    currentTime = time()
    return bool(currentTime - driverLocation[1]['timestamp'] < 5.0)

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

    print("[{}] matchResult: ".format( getTimeStr() ), matchResult)
    
    return matchResult


if __name__ == '__main__':
    startEngine()
