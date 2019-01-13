import redis
from sanic import Sanic
from sanic import response
from asyncio import sleep
import json

from . import constants



# connect to redis
try:
    redisConn = redis.StrictRedis(host='localhost', port=6379)
    print('Connected to redis')
except Exception as ex:
    print('Error:', ex)
    exit('Failed to connect, terminating.')



# setup server
app = Sanic()

async def test_if_alive(request):
    return response.json({
        'message': 'I am alive.',
        'received': request.json
    })

async def realTimeMatch(request):
    rideRequest = redisConn.lpop(constants.REDIS_KEYS__REAL_TIME_RIDE_REQUEST)
    if rideRequest == None:  # when there is no item in list, the result retunrned from redis is None
        return response.json({
            'message': 'No request in Redis'
        })
    
    rideRequest = json.loads(rideRequest)
    response.json({
        'message': 'request received'
    })

    driverLocations = redisConn.hgetall(constants.REDIS_KEYS__DRIVER_LOCATION)
    while True:
        driverLocations = redisConn.hgetall(constants.REDIS_KEYS__DRIVER_LOCATION)
        if len(list(driverLocations.keys())) > 0:
            # has driver, begin matching process
            break
        # no driver yet, wait for it
        print('wait for driver location')
        await sleep(5)
    
    count = 1
    for location in driverLocations:
        print(count, location)
        count += 1

    redisConn.hset(
        constants.REDIS_KEYS__REAL_TIME_RIDE_STATUS, 
        rideRequest['userId'],
        constants.REAL_TIME_RIDE_STATUS__PROCESSING
    )

    return



app.add_route(test_if_alive, '/test-if-alive', methods=['POST'])
app.add_route(realTimeMatch, '/trigger-real-time-match', methods=['POST'])

def run():
    app.run(host="0.0.0.0", port=5000)