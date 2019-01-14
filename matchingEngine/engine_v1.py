import redis
from sanic import Sanic
from sanic import response
from time import sleep, gmtime, strftime, time
import json
import requests

REAL_TIME_RIDE_STATUS__IDLE = 'idle'
REAL_TIME_RIDE_STATUS__IN_QUEUE = 'inQueue'
REAL_TIME_RIDE_STATUS__PROCESSING = 'processing'
REAL_TIME_RIDE_STATUS__ON_RIDE = 'onRide'

REDIS_KEYS__REAL_TIME_RIDE_STATUS = 'realTimeRideStatus'
REDIS_KEYS__REAL_TIME_RIDE_REQUEST = 'realTimeRideRequest'
REDIS_KEYS__DRIVER_LOCATION = 'driverLocation'

SERVER_ENDPOINT = 'http://localhost/notify-match-result/real-time-ride'

def run_match(rideRequest):
    driverLocations = redisConn.hgetall(REDIS_KEYS__DRIVER_LOCATION)
    
    if len(driverLocations) == 0:
        while True:
            # no driver yet, enter wait loop
            currentTimeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print("[{}] wait for active driver".format(currentTimeStr))
            sleep(3)
            driverLocations = redisConn.hgetall(REDIS_KEYS__DRIVER_LOCATION)
            if len(driverLocations) > 0:
                # driver appears, exit wait loop
                break

    # ready to start matching
    driverLocationsList = driverLocations.items()
    redisConn.hset(
        REDIS_KEYS__REAL_TIME_RIDE_STATUS, 
        rideRequest['userId'],
        REAL_TIME_RIDE_STATUS__PROCESSING
    )

    matchResult = find_match(rideRequest, driverLocationsList)
    print('matchResult: ', matchResult)

    requests.post(url = SERVER_ENDPOINT, data = matchResult)


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
    print('rideRequest')
    print('userId', rideRequest['userId'])
    startlatitude = rideRequest['startLocation']['latitude']
    startlongitude = rideRequest['startLocation']['longitude']
    endlatitude = rideRequest['endLocation']['latitude']
    endlongitude = rideRequest['endLocation']['longitude']
    print('start location: lat=', startlatitude, 'long=', startlongitude)
    print('end location: lat=', endlatitude, 'long=', endlongitude)

    for (userId, loc) in driverLocationsList:
        loc = json.loads(loc)
        print('userId', userId)
        latitude = loc['location']['latitude']
        longitude = loc['location']['longitude']
        print('lat=', latitude, 'long=', longitude)
    
    matchResult = {
        'rider': rideRequest,
        'driver': {
            'userId': driverLocationsList[0][0],
            'location': driverLocationsList[0][1]
        },
        'timestamp': time()
    }
    
    return matchResult


if __name__ == '__main__':
    # connect to redis
    try:
        redisConn = redis.StrictRedis(host='localhost', port=6379)
        print('Connected to redis')
    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

    while True:
        rideRequesJSONString = redisConn.lpop(REDIS_KEYS__REAL_TIME_RIDE_REQUEST)
        if rideRequesJSONString == None:
            # when there is no item in list, the result retunrned from redis is None
            currentTimeStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print("[{}] wait for ride request".format(currentTimeStr))
            sleep(3)
        else:
            rideRequest = json.loads(rideRequesJSONString)
            run_match(rideRequest)