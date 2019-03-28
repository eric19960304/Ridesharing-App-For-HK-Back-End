'''
RVGraph
(1) which requests can be pairwise combined: if share > single route then don't pairwise else pair wise
if v->a > v->b then v->b else v->a

for v in V:
    for v2 in V - {v}:
        


(2) which vehicles can serve which requests individually, given their current passengers
for each driver:
    for each request:
        if getDistance(driverLocation, requestLocation) < 1:
            pair driver & request





return data structure example
{
'A':[(140,'S'),(118,'T'),(75,'Z')],
'Z':[(75,'A'),(71,'O')],
'O':[(151,'S'),(71,'Z')],
'T':[(118,'A'),(111,'L')],
'L':[(70,'M'),(111,'T')],
'M':[(75,'D'),(70,'L')], 
'D':[(120,'C'),(75,'M')],
'S':[(140,'A'),(99,'F'),(151,'O'),(80,'R')], 
'R':[(146,'C'),(97,'P'),(80,'S')],
'C':[(120,'D'),(138,'P'),(146,'R')], 
'F':[(211,'B'),(99,'S')],
'P':[(101,'B'),(138,'C'),(97,'R')],
'B':[]
}

'''
import redis
from time import sleep, gmtime, strftime, time
import ujson
import requests
from googleMapApiAdapter import getDistance, getDistanceMatrix

# redis key name, refer to README for the data struture
RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

class RVGraph:
    def __init__(self):
        self.rvGraph = {}
        self.requestsGraph = {}
    
    def RVGraphPairwiseRequests(rideRequest):
        for (riderId, riderLocationJson) in rideRequest:
            for (riderId2, riderLocationJson2) in rideRequest:
                if riderId == riderId2:
                    continue
                #create location List contain two requests' start and end point
                locationList = []
                locationList.append( riderLocationJson[startLocation] )
                locationList.append( riderLocationJson2[startLocation] )
                locationList.append( riderLocationJson[endLocation] )
                locationList.append( riderLocationJson2[endLocation] )
                #calculate the matrix with those four points
                distanceMatrix = getDistanceMatrix(locationList, locationList)
                spearatedRideDistance = distanceMatrix[0][3] + distanceMatrix[1][4]
                for i in range(0,2):
                    for j in range(1, -1, -1):
                        if i == j:
                            continue
                        for k in range(2,4):
                            for l in range(3, 1, -1):
                                if k == l:
                                    continue
                                shareRideDistance = distanceMatrix[i][j] + distanceMatrix[j][k] + distanceMatrix[k][l]
                                if shareRideDistance < spearatedRideDistance:
                                    #add edge between this two points
                                


                

    def RVGraphPairwiseDriverRequest(rideRequest, driverLocationsList):
        driverOnGoing = redisConn.hgetall(DRIVER_ON_GOING_RIDE)
        for (driverId, driverLocationJson) in driverLocationsList:
            if driverId not in driverOnGoing:
                self.rvGraph[driverId] = []
                for (riderId, riderLocationJson) in rideRequest:
                    riderDriverDistance, riderDriverTime = getDistance(locationJson, riderLocationJson)
                    if riderDriverDistance < 2:
                        self.rvGraph[driverId].append( (riderId, riderDriverDistance) )
            else:
                driverPassagerJSON = driverOnGoing[driverId]
                #maximum capicity is 4
                if len(driverPassagerJSON) < 4:
                    #compare distance of path from vechical to two requests' start and end point