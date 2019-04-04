import redis
import ujson

RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

def prettyPrint(data):
    print(ujson.dumps(data, indent=2))

def prettyPrint2(key, data):
    print(key, ujson.dumps(data, indent=2))

def printAllDetails():
    try:
        redisConn = redis.StrictRedis(
            host='localhost',
            port=6379)


        rideRequest = redisConn.lrange(RIDE_REQUEST, 0, -1)
        driverLocationDict = redisConn.hgetall(DRIVER_LOCATION)
        ongoingRideListDict = redisConn.hgetall(DRIVER_ON_GOING_RIDE)

        print('realTimeRideRequest: ')
        requests = [ ujson.loads(r)  for r in rideRequest ]
        for r in requests:
            prettyPrint(r)
        
        print("\ndriverLocation: ")
        for (driverId, locationJson) in driverLocationDict.items():
            location = ujson.loads( locationJson )
            prettyPrint2(driverId, location)

        print("\ndriverOngoingRide: ")
        for (driverId, ongoingRideListJson) in ongoingRideListDict.items():
            onGoingRideList = ujson.loads( ongoingRideListJson )
            prettyPrint2(driverId, onGoingRideList)

    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

if __name__ == "__main__":
    printAllDetails()