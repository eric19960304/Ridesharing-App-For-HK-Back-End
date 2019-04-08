from random import randint
from greedyMatcher import GreedyMatcher
from dynamicTripVehicleAssignmentMatcher import DynamicTripVehicleAssignmentMatcher
from utils import gridWorldDistance, gridWorldDistanceMatrix
from itertools import combinations, permutations
class GridWorldSimulator:
    '''
    requests format:
        [{  
            "id": string,
            "userId": string,
            "startLocation": (int, int),
            "endLocation": (int, int),
            "isOnCar": False,
            "requestedDate" ? : int,
            "matchedDate" ? : int,
            "finishedDate" ? : int
        }]
    drivers format:
    [{
        "userId": string,
        "location":  (int, int),
        "ongoingRide": [ requests ],
        "capacity": number,
    }]

    Note: ? means the field will appear if some conditions are satisfied
    '''

    def __init__(
        self, gridWorldSize, constraints_param, 
        requestGenDuration, maxNumOfRequestsGenPerRound, 
        numOfDrivers, capacity, matchEngineTriggerInterval, algo
        ):
        self.gridWorldSize = gridWorldSize
        self.constraints_param = constraints_param
        self.requestGenDuration = requestGenDuration
        self.maxNumOfRequestsGenPerRound = maxNumOfRequestsGenPerRound
        self.reqId = 0
        self.driverId = 0
        self.requests = []
        self.drivers = []
        self.currentTime = 0
        self.matchingRates = []
        self.numOfDrivers = numOfDrivers
        self.finishedRequests = []
        self.capacity = capacity
        self.totalRequestCount = 0
        self.matchEngineTriggerInterval = matchEngineTriggerInterval
        if algo=='greedy':
            self.matcher = GreedyMatcher(self.constraints_param, useGridWorld=True)
        else:
            self.matcher = DynamicTripVehicleAssignmentMatcher(self.constraints_param, useGridWorld=True)

    def startSimulator(self):

        self.drivers = []

        for i in range(self.numOfDrivers):
            x = randint(0, self.gridWorldSize-1)
            y = randint(0, self.gridWorldSize-1)
            initLoc = (x,y)
            self.drivers.append( Driver(finishedRequestsRef=self.finishedRequests, \
                userId=i, initialLocation=initLoc, capacity=self.capacity, gridWorldSize=self.gridWorldSize) )

        drivers = [ d.getDriver() for d in self.drivers ]
        
        
        # calculate avg distance of pairwise drivers' initial locations
        driversLocations = [ d['location'] for d in drivers ]
        driverInitLocationPairs = list(combinations(driversLocations, 2))
        locationAvgDistance = 0
        for (s1, s2) in driverInitLocationPairs:
            locationAvgDistance += gridWorldDistance(s1, s2)
        locationAvgDistance /= len(driverInitLocationPairs)
        print('avg distance of pairwise drivers\' locations:', locationAvgDistance)

        while True:
            # detect if all requets matched
            if self.currentTime >= self.requestGenDuration and len(self.requests)==0 and len(self.finishedRequests)==self.totalRequestCount:
                break

            if self.currentTime < self.requestGenDuration:
                self._generateRandomRequests()
            
            if self.currentTime%self.matchEngineTriggerInterval==0 and len(self.requests)>0:

                print('[time=%d]'%(self.currentTime))
                numOfRequest = len(self.requests)

                mappings, remainingRequests = self.matcher.match(self.requests, drivers, self.currentTime)
                self.requests = remainingRequests

                for (req, driver) in mappings:
                    req['matchedDate'] = self.currentTime
                    driverIdx = int(driver['userId'])
                    self.drivers[driverIdx].updateRoute()

                # print stat
                numOfMatchedReq = numOfRequest-len(remainingRequests)
                matchRate = numOfMatchedReq / numOfRequest
                self.matchingRates.append(matchRate)
                print( "match rate=%.3f, matched/unmatched requests: %d/%d"%(matchRate, len(mappings), len(remainingRequests)) )
            
            # move all drivers
            for d in self.drivers:
                d.move(self.currentTime)
            
            # increment time
            self.currentTime += 1
        
        print('num of finished/unmatched/total requests: %d/%d/%d' % (len(self.finishedRequests), len(self.requests), self.totalRequestCount))

    def _generateRandomRequests(self):
        '''
        return list of points, size is randomized between [1, maxNumOfRequestsGenPerRound-1]
        '''
        startPoints = set()
        endPoints = set()
        numOfRequests = randint(0, self.maxNumOfRequestsGenPerRound)
        self.totalRequestCount += numOfRequests

        # print('generating %d requests'%(numOfRequests))
        for _ in range(numOfRequests):
            while True:
                startX = randint(0, self.gridWorldSize-1)
                startY = randint(0, self.gridWorldSize-1)
                endX = randint(0, self.gridWorldSize-1)
                endY = randint(0, self.gridWorldSize-1)
                if (startX, startY) != (endX, endY) and \
                    (startX, startY) not in startPoints and \
                    (endX, endY) not in endPoints:
                    startPoints.add( (startX, startY) )
                    endPoints.add( (endX, endY) )
                    break
        startPoints = list(startPoints)
        endPoints = list(endPoints)
        startEndPoints = zip(startPoints, endPoints)
        avgDistance = 0
        for (startPoint, endPoint) in startEndPoints:
            self.requests.append({
                "id": str(self.reqId),
                "userId": str(self.reqId),
                "startLocation": startPoint,
                "endLocation": endPoint,
                "requestedDate": self.currentTime,
                "isOnCar": False,
            })
            self.reqId += 1
            avgDistance += gridWorldDistance(startPoint, endPoint)
        
        # print('avg travel distance: ', avgDistance/len(startPoints))

        # startPointsPairs = list(combinations(startPoints, 2))
        # startPointAvgDistance = 0
        # for (s1, s2) in startPointsPairs:
        #     startPointAvgDistance += gridWorldDistance(s1, s2)
        # startPointAvgDistance /= len(startPointsPairs)
        # print('avg distance between startPoints', startPointAvgDistance)

        # endPointsPairs = list(combinations(endPoints, 2))
        # endPointAvgDistance = 0
        # for (e1, e2) in endPointsPairs:
        #     endPointAvgDistance += gridWorldDistance(e1, e2)
        # endPointAvgDistance /= len(endPointsPairs)
        # print('avg distance between endPoints', endPointAvgDistance)


class Driver:
    def __init__(self, finishedRequestsRef, userId, initialLocation, capacity, gridWorldSize):
        self.finishedRequestsRef = finishedRequestsRef
        self.driver = {
            "userId": str(userId),
            "location":  initialLocation,
            "ongoingRide": [],
            "capacity": capacity,
        }
        self.route = []
        self.gridWorldSize = gridWorldSize

    def getDriver(self):
        return self.driver
    
    def move(self, currentTime):
        # check if arrived next route point
        if len(self.route) > 0 and self.driver['location']==self.route[0]:
            self.route.pop(0)

        # detect start and end ride
        for ride in self.driver['ongoingRide']:
            if self.driver['location']==ride['startLocation'] and (not ride['isOnCar']):
                # print(self.driver['userId'], 'start ride')
                ride['isOnCar'] = True

            if self.driver['location']==ride['endLocation'] and ride['isOnCar']:
                # print(self.driver['userId'], 'end ride')
                ride['finishedDate'] = currentTime
                self.finishedRequestsRef.append(ride)
                self.driver['ongoingRide'].remove(ride)
                # print('ongoing after end: ', self.driver['ongoingRide'])
                self.updateRoute()

        # move
        if len(self.driver['ongoingRide'])==0:
            # move random direction
            (x, y) = self.driver['location']
            possibleMoves = [ (x+1, y), (x-1, y), (x, y+1), (x, y-1) ]
            possibleMoves = [ move for move in possibleMoves 
                if move[0]>=0 and move[0]<self.gridWorldSize and move[1]>=0 and move[1]<self.gridWorldSize
            ]
            newLoc = possibleMoves[randint(0, len(possibleMoves)-1)]
            self.driver['location'] = newLoc
        else:
            # move to next point in route
            if len(self.route)==0:
                self.updateRoute()
            (x_,y_) = self.route[0]
            (x,y) = self.driver['location']
            # always try to align x axis first
            if x!=x_:
                if x < x_:
                    self.driver['location'] = (x+1, y)
                else:
                    self.driver['location'] = (x-1, y)
            else:
                if y < y_:
                    self.driver['location'] = (x, y+1)
                else:
                    self.driver['location'] = (x, y-1)

    def updateRoute(self):
        '''
        find best route among all the ongoingRides, and save it to self.route

        origins, destinations = [ ongoingRides starts and ends , driverLoc ]
        '''
        origins = []
        for ongoingRide in self.driver['ongoingRide']:

            if 'isOnCar' not in ongoingRide:
                ongoingRide['isOnCar'] = False

            if ongoingRide['isOnCar']:
                end = ongoingRide['endLocation']
                origins.append(end)
            else:
                start = ongoingRide['startLocation']
                end = ongoingRide['endLocation']
                origins.append(start)
                origins.append(end)
        numOfReqLocations = len(origins)
        origins.append(self.driver['location'])
        
        # corner case
        if numOfReqLocations==1:
            self.route = [origins[0]]
            return
        if numOfReqLocations==0:
            self.route = []
            return

        distMatrix = gridWorldDistanceMatrix(origins, origins)
        
        # calculate the cost fo all possible routes among ongoingRides
        possible_cost_bestRoutes = []
        pathLen = numOfReqLocations
        for path in permutations(list(range(pathLen))):
            cost = distMatrix[-1][path[0]] # driver -> first point in path
            for i in range(pathLen-1):
                cost += distMatrix[ path[i] ][ path[i+1] ]
            possible_cost_bestRoutes.append( (cost, path) )
        
        # print('possible_cost_bestRoutes', possible_cost_bestRoutes)
    
        (bestRouteCost, bestRoutePath) = min(possible_cost_bestRoutes)
        # print(bestRoutePath)
        
        newRoute = []
        for i in bestRoutePath:
            newRoute.append( origins[i] )
        self.route = newRoute


if __name__ == '__main__':

    gridWorld = GridWorldSimulator(
        gridWorldSize=100, 
        constraints_param={ 
            'maxMatchDistance': 25,
            'maxWaitingTime': 25,
        }, 
        requestGenDuration=50, 
        maxNumOfRequestsGenPerRound=10, 
        numOfDrivers=30,
        capacity=2,
        matchEngineTriggerInterval=10,
        algo='greedy'
    )
    gridWorld.startSimulator()
