import redis
from time import sleep, gmtime, strftime, time
from greedyMatcher import GreedyMatcher


def startSimulator():

    matcher = GreedyMatcher({ 'maxMatchDistance': 2 })
    gridWorldSize = 1000

    for currentTime in range(1, 101):
        
        if len(requests)>0 and len(drivers)>0:
            try:
                # match
                mappings, remainingRequests = matcher.match(requests, drivers)

                print("[{}] : ".format( getTimeStr() ), 'mapping (passenger->driver): ')
                for q, d in mappings:
                    print("  %s -> %s" %(q['userId'], d['userId']))
                print('remaining requests: ', len(remainingRequests))

                for mapping in mappings:
                    r, d = mapping
                    matchResult = {
                        "rider": r,
                        "driver": {
                            "userId": d['userId'],
                            "location": d['location']
                        },
                        "timestamp": time(),
                        "algoVersion": ALGO_VERSION
                    }
                    requestsClient.post(url = SERVER_ENDPOINT, json = matchResult)
                # end of for
            except Exception as e:
                # push back the unhandled requests
                requestsJsons = [ ujson.dumps(r) for r in requests ]
                redisConn.rpush(RIDE_REQUEST, *requestsJsons)
                raise e
            
            # push back the unhandled requests
            if len(remainingRequests)>0:
                remainingRequestJsons = [ ujson.dumps(r) for r in remainingRequests ]
                redisConn.rpush(RIDE_REQUEST, *remainingRequestJsons)
            # end of if
            
        # end of if
    # end of while


def isDriverOnline(driverLocation):
    # print("[{}] : ".format( getTimeStr() ), ' location time: ', driverLocation['timestamp'])
    currentTime = time()*1000
    return bool(currentTime - float(driverLocation['timestamp']) <= 7000.0)


if __name__ == '__main__':
    startSimulator()
