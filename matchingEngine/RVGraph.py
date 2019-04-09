'''
RVGraph
(1) which requests can be pairwise combined: if share > single route then don't pairwise else pair wise
(2) which vehicles can serve which requests individually, given their current passengers
'''

from time import sleep, gmtime, strftime, time

from googleMapApiAdapter import getDistance, getDistanceMatrix
from utils import gridWorldDistance, gridWorldDistanceMatrix

# redis key name, refer to README for the data struture
RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

class RVGraph:
    def __init__(self, constraints_param, useGridWorld=False):
        '''
        constraints_param format:
        {
            # max distance between driver's location and request's start point allowed to be matched
            "maxMatchDistance": number    
        }
        '''
        self.rvGraph = []
        self.requestsGraph = []  
        self.maxMatchDistance = constraints_param['maxMatchDistance']
        self.useGridWorld = useGridWorld              

    def _getDistanceMatrix(self, origins, destinations):
        if self.useGridWorld:
            return gridWorldDistanceMatrix(origins, destinations)
        else:
            return getDistanceMatrix(origins, destinations)
    
    def _getDistance(self, origin, destination):
        if self.useGridWorld:
            return gridWorldDistance(origin, destination)
        else:
            return getDistance(origin, destination)               

    def satifiedAllConstraints(self, minShareDistance, separatedDistance, waitingDistance):
        if minShareDistance > separatedDistance:
            return True
        #waitingTime: self.maxMatchDistance
        if waitingDistance < self.maxMatchDistance:
            return True
        return False

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
    [
        ('request1', 'request2'),
        ('request1', 'request3')
    ]
    '''

    def RVGraphPairwiseRequests(self, rideRequests):
        for request in rideRequests:
            for request2 in rideRequests:
                if (request, request2) in self.requestsGraph or (request2, request) in self.requestsGraph:
                    continue
                if request == request2:
                    continue
                #create location List contain two requests' start and end point
                locationList = []
                locationList.append( request["startLocation"] )
                locationList.append( request2["startLocation"] )
                locationList.append( request["endLocation"] )
                locationList.append( request2["endLocation"] )
                #calculate the matrix with those four points
                distanceMatrix = self._getDistanceMatrix(locationList, locationList)
                spearatedRideDistance = distanceMatrix[0][2] + distanceMatrix[1][3]

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
                    self.requestsGraph.append( (request, request2) )
                                


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
    (driver, request, delayDistance)
    [(driver1','request1', 140), ('driver1','request2', 118),('driver1','request3', 75) , ('driver2','request1', 172)]
    '''

    '''TSP Link:https://pypi.org/project/tsp/'''

    def RVGraphPairwiseDriverRequest(self, rideRequests, driverList):
        

        for driver in driverList:
            edgeList = []

            #need to test
            if len(driver["ongoingRide"]) == 0:
                
                for request in rideRequests:
                    riderDriverDistance = self._getDistance(driver["location"], request["startLocation"])

                    #delay: self.maxMatchDistance
                    if riderDriverDistance < self.maxMatchDistance:
                        edgeList.append( (driver, request, riderDriverDistance) )
            else:
                driverPassagerList = driver["ongoingRide"]

                #maximum capicity is 2
                if len(driver["ongoingRide"]) < 2:
                    #TWO RIDERS ONLY
                    passagerLocationList = []
                    #request is not on ride
                    if not driverPassagerList[0]["isOnCar"]:
                        passagerLocationList.append(driverPassagerList[0]["startLocation"])
                    passagerLocationList.append(driverPassagerList[0]["endLocation"])
                    for request in rideRequests:
                        locationList = []
                        locationList.append(request["startLocation"])
                        locationList.append(request["endLocation"])
                        locationList.append(driver['location'])
                        locationList += passagerLocationList
                        
                        distanceMatrix = self._getDistanceMatrix(locationList, locationList)

                        delayDistance = float('inf')
                        waitingDistance = float('inf')
                        minShareDistance = float('-inf')

                        if not driverPassagerList[0]["isOnCar"]:
                            #0: request startLocation, 1: request endLocation, 2: driver Location, 3: passager startLocation, 4: passager endLocation
                            minShareDistance = min([distanceMatrix[2][0] + distanceMatrix[0][3] + distanceMatrix[3][4] + distanceMatrix[4][1],
                            distanceMatrix[2][0] + distanceMatrix[0][3] + distanceMatrix[3][1] + distanceMatrix[1][4],
                            distanceMatrix[2][3] + distanceMatrix[3][0] + distanceMatrix[0][4] + distanceMatrix[4][1],
                            distanceMatrix[2][3] + distanceMatrix[3][0] + distanceMatrix[0][1] + distanceMatrix[1][4]])

                            delayDistance = minShareDistance - distanceMatrix[2][3] - distanceMatrix[3][4] 
                            waitingDistance = min(distanceMatrix[2][0], distanceMatrix[2][3])
                        else:
                            #0: request startLocation, 1: request endLocation, 2: driver Location, 3: passager endLocation
                            minShareDistance = min(distanceMatrix[2][0] + distanceMatrix[0][1] + distanceMatrix[1][3],
                            distanceMatrix[2][0] + distanceMatrix[0][3] + distanceMatrix[3][1])

                            delayDistance = minShareDistance - distanceMatrix[2][3] - distanceMatrix[0][1]
                            waitingDistance = min(distanceMatrix[2][0], distanceMatrix[2][3])

                        if self.satifiedAllConstraints(minShareDistance, separatedDistance, waitingDistance):
                            edgeList.append( (driver, request, delayDistance) )

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
                        
            self.rvGraph += edgeList

# def startEngine():
#     # connect to redis
#     try:
#         redisConn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
#         print('Connected to redis')
#     except Exception as ex:
#         print('Error:', ex)
#         exit('Failed to connect, terminating.')

#     requests = []
#     drivers = []

#     # get all driver locations
#     driverLocationDict = redisConn.hgetall(DRIVER_LOCATION)
#     for (driverId, locationJson) in driverLocationDict.items():
#             location = ujson.loads( locationJson )

#             if( isDriverOnline(location) ):
#                 ongoingRideListJson = redisConn.hget(DRIVER_ON_GOING_RIDE, driverId)
#                 if(ongoingRideListJson!=None):
#                     ongoingRideList = ujson.loads(ongoingRideListJson)
#                 else:
#                     ongoingRideList = []
#                 # print(len(ongoingRideList))

#                 drivers.append({
#                     "userId": driverId,
#                     "location": location['location'],
#                     "capacity": 4,
#                     "ongoingRide": ongoingRideList
#                 })
#             # end of if
#         # end of for

#     #driverOnGoing = redisConn.hgetall(DRIVER_ON_GOING_RIDE)

#     # get all requests
#     rideRequest = redisConn.lrange(RIDE_REQUEST, 0, -1)
#     numOfReq = len(rideRequest)

#     # remove the received request
#     redisConn.ltrim(RIDE_REQUEST, numOfReq, -1)
#     requests = [ ujson.loads(r) for r in rideRequest ]
#     #print(requests)

#     rvGraph = RVGraph()
#     # rvGraph.RVGraphPairwiseRequests(requests)
#     rvGraph.RVGraphPairwiseDriverRequest(requests, drivers)

# def isDriverOnline(driverLocation):
#     # print("[{}] : ".format( getTimeStr() ), ' location time: ', driverLocation['timestamp'])
#     currentTime = time()*1000
#     return bool(currentTime - float(driverLocation['timestamp']) <= 7000.0)

# if __name__ == '__main__':
#     startEngine()