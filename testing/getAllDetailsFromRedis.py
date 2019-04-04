import redis
import ujson

RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

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
            print(ujson.dumps(r, indent=4))
        
        print("\ndriverLocation: ")
        for (driverId, locationJson) in driverLocationDict.items():
            print(driverId, ':', ujson.dumps(ujson.loads( locationJson ), indent=4))

        print("\ndriverOngoingRide: ")
        for (driverId, ongoingRideListJson) in ongoingRideListDict.items():
            print(driverId, ':', ujson.dumps(ujson.loads( ongoingRideListJson ), indent=4))

    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

if __name__ == "__main__":
    printAllDetails()