import redis
from sanic import Sanic
from sanic import response
from time import sleep, gmtime, strftime, time
import ujson
import requests

REAL_TIME_RIDE_STATUS__IDLE = 'idle'
REAL_TIME_RIDE_STATUS__IN_QUEUE = 'inQueue'
REAL_TIME_RIDE_STATUS__PROCESSING = 'processing'
REAL_TIME_RIDE_STATUS__ON_RIDE = 'onRide'

REDIS_KEYS__REAL_TIME_RIDE_STATUS = 'realTimeRideStatus'
REDIS_KEYS__REAL_TIME_RIDE_REQUEST = 'realTimeRideRequest'
REDIS_KEYS__DRIVER_LOCATION = 'driverLocation'

SERVER_ENDPOINT = 'http://localhost/notify-match-result/real-time-ride'

def startEngine():
    # connect to redis
    try:
        redisConn = redis.StrictRedis(host='localhost', port=6379)
        print('Connected to redis')
        redisConn.flushall()
        print('Flush All Cache')
    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

    currentTimeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("[{}] wait for ride request".format(currentTimeStr))
    while True:
        rideRequestJSONString = redisConn.lpop(REDIS_KEYS__REAL_TIME_RIDE_REQUEST)
        if rideRequestJSONString == None:
            # when there is no item in list, the result retunrned from redis is None
            sleep(3)
        else:
            rideRequest = ujson.loads( rideRequestJSONString.decode('utf-8') )
            run_match(rideRequest)

def run_match(rideRequest):
    driverLocationsDirty = redisConn.hgetall(REDIS_KEYS__DRIVER_LOCATION)
    
    currentTimeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("[{}] wait for active driver".format(currentTimeStr))

    if len(driverLocationsDirty) == 0:
        while True:
            # no driver yet, enter wait loop
            sleep(3)
            driverLocationsDirty = redisConn.hgetall(REDIS_KEYS__DRIVER_LOCATION)
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
    redisConn.hset(
        REDIS_KEYS__REAL_TIME_RIDE_STATUS, 
        rideRequest['userId'],
        REAL_TIME_RIDE_STATUS__PROCESSING
    )

    matchResult = find_match(rideRequest, list(driverLocations.items()))
    requests.post(url = SERVER_ENDPOINT, json = matchResult)


def find_match(rideRequest, driverLocationsList):
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

    for (userId, loc) in driverLocationsList:
        print('userId', userId)
        latitude = loc['location']['latitude']
        longitude = loc['location']['longitude']
        print('lat=', latitude, 'long=', longitude)

    matchResult = {
        "rider": rideRequest,
        "driver": {
            "userId": driverLocationsList[0][0],
            "location": driverLocationsList[0][1]['location'],
            "timestamp": driverLocationsList[0][1]['timestamp']
        },
        "timestamp": time()
    }
    
    return matchResult


if __name__ == '__main__':
    startEngine()