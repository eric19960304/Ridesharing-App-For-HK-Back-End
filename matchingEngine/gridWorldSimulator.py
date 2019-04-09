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
            "startedRideDate" ? : int,
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

    def __init__(self, gridWorldH, gridWorldW, constraints_param, requetSeq, numOfDrivers, 
        capacity, matchEngineTriggerInterval, algo, showDetails=False):
        '''
        For each time unit t, the simulator will bring all the requets in requetSeq[t] to the simulation
        requetSeq format: 
        [ [request] ]
        '''
        self.gridWorldH = gridWorldH
        self.gridWorldW = gridWorldW
        self.constraints_param = constraints_param
        self.requetSeq = requetSeq
        self.numOfDrivers = numOfDrivers
        self.capacity = capacity
        self.matchEngineTriggerInterval = matchEngineTriggerInterval
        self.showDetails = showDetails
        
        # non param instance variables

        if algo=='greedy':
            self.matcher = GreedyMatcher(self.constraints_param, useGridWorld=True)
        else:
            self.matcher = DynamicTripVehicleAssignmentMatcher(self.constraints_param, useGridWorld=True)
        
        self.requests = []
        self.drivers = []
        self.finishedRequests = []
        self.matchingRates = []
        self.shareRates = []

        self.currentTime = 0
        self.totalRequestCount = 0
        self.driverId = 0
        

    def startSimulator(self):

        self.drivers = []

        for i in range(self.numOfDrivers):
            x = randint(0, self.gridWorldW-1)
            y = randint(0, self.gridWorldH-1)
            initLoc = (x,y)
            self.drivers.append( Driver(finishedRequestsRef=self.finishedRequests, \
                userId=i, initialLocation=initLoc, capacity=self.capacity, \
                gridWorldH=self.gridWorldH, gridWorldW=self.gridWorldW) )

        drivers = [ d.getDriver() for d in self.drivers ]
        
        
        # calculate avg distance of pairwise drivers' initial locations
        driversLocations = [ d['location'] for d in drivers ]
        driverInitLocationPairs = list(combinations(driversLocations, 2))
        locationAvgDistance = 0
        for (s1, s2) in driverInitLocationPairs:
            locationAvgDistance += gridWorldDistance(s1, s2)
        locationAvgDistance /= len(driverInitLocationPairs)
        print('Average distance of pairwise drivers\' locations:', locationAvgDistance)

        while True:
            # detect if all requets matched
            if self.currentTime >= len(self.requetSeq)  and len(self.requests)==0 and len(self.finishedRequests)==self.totalRequestCount:
                break

            if self.currentTime < len(self.requetSeq):
                self.totalRequestCount += len(self.requetSeq[self.currentTime])
                self.requests.extend( self.requetSeq[self.currentTime] )
            
            if self.currentTime%self.matchEngineTriggerInterval==0 and len(self.requests)>0:
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
                print("[t=%d] match rate=%.3f, matched/unmatched/finished/total requests: %d/%d/%d/%d" % \
                    (self.currentTime, matchRate, len(mappings), len(remainingRequests), \
                    len(self.finishedRequests), self.totalRequestCount) )
            
            # move all drivers
            for d in self.drivers:
                d.move(self.currentTime, self.showDetails)
            
            # increment time
            self.currentTime += 1
        print('[t=%d] Finished all rides'%(self.currentTime))
        print('Num of finished/unmatched/total requests: %d/%d/%d' % (len(self.finishedRequests), len(self.requests), self.totalRequestCount))
class Driver:
    def __init__(self, finishedRequestsRef, userId, initialLocation, capacity, gridWorldW, gridWorldH):
        self.finishedRequestsRef = finishedRequestsRef
        self.driver = {
            "userId": str(userId),
            "location":  initialLocation,
            "ongoingRide": [],
            "capacity": capacity,
        }
        self.route = []
        self.gridWorldW = gridWorldW
        self.gridWorldH = gridWorldH

    def getDriver(self):
        return self.driver
    
    def move(self, currentTime, showDetails=False):
        # check if arrived next route point
        if len(self.route) > 0 and self.driver['location']==self.route[0]:
            self.route.pop(0)

        # detect start and end ride
        for ride in self.driver['ongoingRide']:
            if self.driver['location']==ride['startLocation'] and (not ride['isOnCar']):
                if showDetails:
                    print('[t=%d] R%s is now on car (D%s)'%(currentTime, ride['userId'], self.driver['userId']))
                
                ride['isOnCar'] = True
                ride['startedRideDate'] = currentTime

            if self.driver['location']==ride['endLocation'] and ride['isOnCar']:
                if showDetails:
                    print('[t=%d] R%s arrived dest (D%s)'%(currentTime, ride['userId'], self.driver['userId']))
                ride['finishedDate'] = currentTime
                
                self.finishedRequestsRef.append(ride)
                self.driver['ongoingRide'].remove(ride)
                self.updateRoute()

        # move
        if len(self.driver['ongoingRide'])==0:
            # move random direction
            (x, y) = self.driver['location']
            possibleMoves = [ (x+1, y), (x-1, y), (x, y+1), (x, y-1) ]
            possibleMoves = [ move for move in possibleMoves 
                if move[0]>=0 and move[0]<self.gridWorldW and move[1]>=0 and move[1]<self.gridWorldH
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
    
        (_, bestRoutePath) = min(possible_cost_bestRoutes)
        # print(bestRoutePath)
        
        newRoute = []
        for i in bestRoutePath:
            newRoute.append( origins[i] )
        self.route = newRoute


def generateRequetSeq(gridWorldW, gridWorldH, numOfSeq, maxNumOfRequestsPerSeq):
    requestSeq = []
    totalRequestCount = 0
    reqId = 0

    for i in range(numOfSeq):
        requests = []
        startPoints = set()
        endPoints = set()
        numOfRequests = randint(0, maxNumOfRequestsPerSeq)
        totalRequestCount += numOfRequests

        for _ in range(numOfRequests):
            while True:
                startX = randint(0, gridWorldW-1)
                startY = randint(0, gridWorldH-1)
                endX = randint(0, gridWorldW-1)
                endY = randint(0, gridWorldH-1)
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
            requests.append({
                "id": str(reqId),
                "userId": str(reqId),
                "startLocation": startPoint,
                "endLocation": endPoint,
                "requestedDate": i,
                "isOnCar": False,
            })
            reqId += 1
            avgDistance += gridWorldDistance(startPoint, endPoint)
        requestSeq.append(requests)
    
    return requestSeq



if __name__ == '__main__':
    '''
    Waiting time= T_pickup - T_request
    total travel delay = T_drop - T*_arrive
        where T*_arrive the earliest possible time at which the destination could be reached
    '''
    gridWorldH = 30
    gridWorldW = 90
    numOfRoundToGenerateReq = 100
    maxNumOfReqGeneratePerRound = 3

    # generate requets for all rounds
    requetSeq = generateRequetSeq(gridWorldH, gridWorldW, numOfRoundToGenerateReq, maxNumOfReqGeneratePerRound)

    gridWorld = GridWorldSimulator(
        gridWorldH=30,
        gridWorldW=90,
        constraints_param={ 
            'maxMatchDistance': 25,
            'maxWaitingTime': 25,
        }, 
        requetSeq=requetSeq,
        numOfDrivers=30,
        capacity=3,
        matchEngineTriggerInterval=10,
        algo='greedy',
        showDetails=False
    )
    gridWorld.startSimulator()
