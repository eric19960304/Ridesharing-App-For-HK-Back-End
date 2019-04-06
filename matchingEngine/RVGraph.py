'''
RVGraph
(1) which requests can be pairwise combined: if share > single route then don't pairwise else pair wise
(2) which vehicles can serve which requests individually, given their current passengers
'''
import redis
from time import sleep, gmtime, strftime, time
import ujson
from googleMapApiAdapter import getDistance, getDistanceMatrix

# redis key name, refer to README for the data struture
RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

class RVGraph:
    def __init__(self):
        self.rvGraph = {}
        self.requestsGraph = {}                       

    '''
    Input
        requests format:
        [{  "id": string,
            "userId": string,
            "startLocation": {
                "latitude": number,
                "longitude": number
            },
            "endLocation": {
                "latitude": number,
                "longitude": number
            }
            "timestamp": number]

    Output:
    {
        ('request1.userID', 'request2.userID'): distance,
        ('request1.userID', 'request3.userID'): distance,
    }
    '''

    def RVGraphPairwiseRequests(self, rideRequests):
        for riderLocationJson in rideRequests:
            for riderLocationJson2 in rideRequests:
                if (riderLocationJson["userId"], riderLocationJson2["userId"]) in self.requestsGraph or (riderLocationJson2["userId"], riderLocationJson["userId"]) in self.requestsGraph:
                    continue
                if riderLocationJson["userId"] == riderLocationJson2["userId"]:
                    continue
                #create location List contain two requests' start and end point
                locationList = []
                locationList.append( riderLocationJson["startLocation"] )
                locationList.append( riderLocationJson2["startLocation"] )
                locationList.append( riderLocationJson["endLocation"] )
                locationList.append( riderLocationJson2["endLocation"] )
                #calculate the matrix with those four points
                distanceMatrix = getDistanceMatrix(locationList, locationList)
                spearatedRideDistance = distanceMatrix[0][3] + distanceMatrix[1][4]

                possibleDistance = []
                for i in range(0,2):
                    for j in range(1, -1, -1):
                        if i == j:
                            continue
                        for k in range(2,4):
                            for l in range(3, 1, -1):
                                if k == l:
                                    continue
                                pathDistance = distanceMatrix[i][j] + distanceMatrix[j][k] + distanceMatrix[k][l]
                                possibleDistance.append( pathDistance )
                shareRideDistance = min(possibleDistance)

                if shareRideDistance < spearatedRideDistance:
                    self.requestsGraph[(riderLocationJson["userId"], riderLocationJson2["userId"])] = shareRideDistance
        #print(self.requestsGraph)
                                


    '''
    Input
        requests format:
        [{  "id": string,
            "userId": string,
            "startLocation": {
                "latitude": number,
                "longitude": number
            },
            "endLocation": {
                "latitude": number,
                "longitude": number
            }
            "timestamp": number]
        
        drivers format:
        [{  "userId": string,
            "location":  {
                "latitude": number,
                "longitude": number
            },
            "ongoingRide": [ requests ],
            "capacity": number,
            "timestamp": number           }]

    return data structure example
    {
               (userID, delayDistance)
    'driver1':[('request1', 140),('request2', 118),('request3', 75)],
    'driver2':[('request1', 172),('request2', 220)],
    }
    '''

    '''TSP Link:https://pypi.org/project/tsp/'''

    def RVGraphPairwiseDriverRequest(self, rideRequests, driverList):
        

        for driverJson in driverList:
            edgeList = []

            #need to test
            print(driverJson["ongoingRide"])
            print(len(driverJson["ongoingRide"]))
            if len(driverJson["ongoingRide"]) == 0:
                
                for riderLocationJson in rideRequests:
                    riderDriverDistance = getDistance(driverJson["location"], riderLocationJson["startLocation"])
                    if riderDriverDistance < 5000:
                        edgeList.append( (riderLocationJson["userId"], riderDriverDistance) )
            else:
                driverPassagerList = driverJson["ongoingRide"]

                #maximum capicity is 2

                if len(driverJson["ongoingRide"]) < 2:
                    #TWO RIDERS ONLY
                    passagerLocationList = []
                    #request is not on ride
                    if not driverPassagerList[0]["isOnCar"]:
                        passagerLocationList.append(driverPassagerList[0]["startLocation"])
                    passagerLocationList.append(driverPassagerList[0]["endLocation"])
                    for riderLocationJson in rideRequests:
                        locationList = []
                        locationList.append(riderLocationJson["startLocation"])
                        locationList.append(riderLocationJson["endLocation"])
                        locationList.append(driverJson['location'])
                        locationList += passagerLocationList
                        
                        distanceMatrix = getDistanceMatrix(locationList, locationList)

                        delayDistance = 100000

                        if not driverPassagerList[0]["isOnCar"]:
                            minimumShareDistance = min([distanceMatrix[2][0] + distanceMatrix[0][3] + distanceMatrix[3][4] + distanceMatrix[4][1],
                            distanceMatrix[2][0] + distanceMatrix[0][3] + distanceMatrix[3][1] + distanceMatrix[1][4],
                            distanceMatrix[2][3] + distanceMatrix[3][0] + distanceMatrix[0][4] + distanceMatrix[4][1],
                            distanceMatrix[2][3] + distanceMatrix[3][0] + distanceMatrix[0][1] + distanceMatrix[1][4]])

                            delayDistance = minimumShareDistance - distanceMatrix[2][3] + distanceMatrix[3][4] 
                        else:
                            delayDistance = distanceMatrix[2][0] + distanceMatrix[0][1] + distanceMatrix[2][3] - distanceMatrix[2][3]

                        #delay
                        if delayDistance < 5000:
                            edgeList.append( (riderId, delayDistance) )

                    # passagerLocationList = []
                    # for passagerJson in driverPassagerList:
                    #     if not riverPassagerList[isOnRide]:
                    #         passagerLocationList.append(passagerJson[startLocation])
                    #     passagerLocationList.append(passagerJson[endLocation])
                    # for (riderId, riderLocationJson) in rideRequests:
                    #     locationList = []
                    #     locationList.append(riderLocationJson[startLocation])
                    #     locationList.append(riderLocationJson[endLocation])
                    #     locationList.append(driverLocation)
                        
                    #     distanceMatrix = getDistanceMatrix(locationList, locationList + passagerLocationList)
                    #     #TSP
                        
            self.rvGraph[driverJson["userId"]] = edgeList
        print(self.rvGraph)

def startEngine():
    # connect to redis
    try:
        redisConn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        print('Connected to redis')
    except Exception as ex:
        print('Error:', ex)
        exit('Failed to connect, terminating.')

    requests = []
    drivers = []

    # get all driver locations
    driverLocationDict = redisConn.hgetall(DRIVER_LOCATION)
    for (driverId, locationJson) in driverLocationDict.items():
            location = ujson.loads( locationJson )

            if( isDriverOnline(location) ):
                ongoingRideListJson = redisConn.hget(DRIVER_ON_GOING_RIDE, driverId)
                if(ongoingRideListJson!=None):
                    ongoingRideList = ujson.loads(ongoingRideListJson)
                else:
                    ongoingRideList = []
                # print(len(ongoingRideList))

                drivers.append({
                    "userId": driverId,
                    "location": location['location'],
                    "capacity": 4,
                    "ongoingRide": ongoingRideList
                })
            # end of if
        # end of for

    #driverOnGoing = redisConn.hgetall(DRIVER_ON_GOING_RIDE)

    # get all requests
    rideRequest = redisConn.lrange(RIDE_REQUEST, 0, -1)
    numOfReq = len(rideRequest)

    # remove the received request
    redisConn.ltrim(RIDE_REQUEST, numOfReq, -1)
    requests = [ ujson.loads(r) for r in rideRequest ]
    #print(requests)

    rvGraph = RVGraph()
    # rvGraph.RVGraphPairwiseRequests(requests)

    #print(driverLocationDict)
    rvGraph.RVGraphPairwiseDriverRequest(requests, drivers)

def isDriverOnline(driverLocation):
    # print("[{}] : ".format( getTimeStr() ), ' location time: ', driverLocation['timestamp'])
    currentTime = time()*1000
    return bool(currentTime - float(driverLocation['timestamp']) <= 7000.0)

if __name__ == '__main__':
    startEngine()