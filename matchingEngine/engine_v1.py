import redis
from time import sleep, gmtime, strftime, time
import ujson
import requests

# redis key name, refer to README for the data struture
RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_MATCHED_DETAILS = 'driverMatchedDetail'

SERVER_ENDPOINT = 'http://localhost/notify-match-result/real-time-ride'

def getTimeStr():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def startEngine():
    # connect to redis
    try:
        redisConn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        print('Connected to redis')
    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

    while True:
        
        queueLen = redisConn.llen(RIDE_REQUEST)
        onlineDriverCount =   redisConn.hlen(DRIVER_LOCATION)

        if queueLen > 0 and onlineDriverCount > 0:
            # consume one request from queue
            
            rideRequest = ujson.loads(redisConn.lpop(RIDE_REQUEST))

            # get all driver locations
            driverLocations = redisConn.hgetall(DRIVER_LOCATION)
            for (userId, locationJson) in driverLocations.items():
                location = ujson.loads( locationJson )
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
    print("[{}] matchResult: ".format( getTimeStr() ), ' location time: ', driverLocation['timestamp'])
    currentTime = time()
    return bool(currentTime - driverLocation['timestamp'] < 5.0)

def find_one_match(rideRequest, driverLocationsList):

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
