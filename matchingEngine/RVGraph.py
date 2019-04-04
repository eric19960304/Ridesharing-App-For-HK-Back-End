'''
RVGraph
(1) which requests can be pairwise combined: if share > single route then don't pairwise else pair wise
(2) which vehicles can serve which requests individually, given their current passengers
'''
import redis
from time import sleep, gmtime, strftime, time
import ujson
import requests
import tsp
from googleMapApiAdapter import getDistance, getDistanceMatrix

# redis key name, refer to README for the data struture
RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

'''
{
    ('request1', 'request2'): distance,
    ('request1', 'request3'): distance,
}
'''

class RVGraph:
    def __init__(self):
        self.rvGraph = {}
        self.requestsGraph = {}                       

    def RVGraphPairwiseRequests(self, rideRequests):
        for (riderId, riderLocationJson) in rideRequests:
            for (riderId2, riderLocationJson2) in rideRequests:
                if (riderId, riderId2) in self.requestsGraph or (riderId2, riderId) in self.requestsGraph:
                    continue
                if riderId == riderId2:
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
                    self.requestsGraph[(riderId, riderId2)] = shareRideDistance
                                


    '''
    return data structure example
    {
               (userID, delayDistance)
    'driver1':[('request1', 140),('request2', 118),('request3', 75)],
    'driver2':[('request1', 172),('request2', 220)],
    }
    '''

    '''TSP Link:https://pypi.org/project/tsp/'''

    def RVGraphPairwiseDriverRequest(self, rideRequests, driverLocationsList):
        # connect to redis
        try:
            redisConn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
            print('Connected to redis')
        except Exception as ex:
            print('Error:', ex)
            exit('Failed to connect, terminating.')

        driverOnGoing = redisConn.hgetall(DRIVER_ON_GOING_RIDE)

        for (driverId, driverLocationJson) in driverLocationsList:
            edgeList = []

            #need to test
            if driverId not in driverOnGoing:
                
                for (riderId, riderLocationJson) in rideRequests:
                    riderDriverDistance = getDistance(driverLocationJson, riderLocationJson)
                    edgeList.append( (riderId, riderDriverDistance) )
            else:
                driverPassagerList = driverOnGoing[driverId]

                #maximum capicity is 2

                #create a driver location directory
                driverLocation = {}
                driverLocation["latitude"] = driverLocationJson["location"]["latitude"]
                driverLocation["longitude"] = driverLocationJson["location"]["longitude"]

                if len(driverPassagerList) < 2:
                    #TWO RIDERS ONLY
                    passagerLocationList = []
                    #request is not on ride
                    if not driverPassagerList[0]["isOnRide"]:
                        passagerLocationList.append(driverPassagerList[0]["startLocation"])
                    passagerLocationList.append(driverPassagerList[0]["endLocation"])
                    for (riderId, riderLocationJson) in rideRequests:
                        locationList = []
                        locationList.append(riderLocationJson["startLocation"])
                        locationList.append(riderLocationJson["endLocation"])
                        locationList.append(driverLocation)
                        locationList += passagerLocationList

                        
                        distanceMatrix = getDistanceMatrix(locationList, locationList)

                        delayDistance = 100000

                        if not driverPassagerList[0]["isOnRide"]:
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
                        
            self.rvGraph[driverId] = edgeList
