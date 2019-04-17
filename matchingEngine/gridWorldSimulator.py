from random import randint
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import time

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

    def __init__(self, gridWorldW, gridWorldH, constraints_param, requetSeq, driverLocSeq, driverSpeed, 
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
        self.driverLocSeq = driverLocSeq
        self.driverSpeed = driverSpeed
        self.capacity = capacity
        self.matchEngineTriggerInterval = matchEngineTriggerInterval
        self.showDetails = showDetails
        self.avgWaitingTime = 0
        self.avgtotalDelay = 0
        
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
        self.seatUtilization = []
        self.numOfRemainingRequests = []

        self.currentTime = 1
        self.totalRequestCount = 0
        self.totalDriverCount = 0
        self.nextDriverId = 0
        

    def startSimulator(self, benchmark=False):

        while True:
            # extract request from sequence
            if self.currentTime <= len(self.requetSeq):
                curIdx = self.currentTime - 1
                self.totalRequestCount += len(self.requetSeq[curIdx])
                for r in self.requetSeq[curIdx]:
                    r['isOnCar'] = False
                self.requests.extend( self.requetSeq[curIdx] )
            
            # extract driver from sequence
            if self.currentTime <= len(self.driverLocSeq):
                curIdx = self.currentTime - 1
                self.totalDriverCount += len(self.driverLocSeq[curIdx])
                for loc in self.driverLocSeq[curIdx]:
                    self.drivers.append( Driver(finishedRequestsRef=self.finishedRequests, \
                    userId=self.nextDriverId, initialLocation=loc, \
                    capacity=self.capacity, gridWorldW=self.gridWorldW, gridWorldH=self.gridWorldH) )
                    self.nextDriverId += 0
            

            if (self.currentTime!=1 or benchmark) and (self.currentTime%self.matchEngineTriggerInterval==0 or benchmark) and len(self.requests)>0 and self.currentTime <= len(self.requetSeq):
                numOfRequest = len(self.requests)
                drivers = [ d.getDriver() for d in self.drivers if len(d.getDriver()['ongoingRide']) < 2 ]

                # ******* start match********
                mappings, remainingRequests = self.matcher.match(self.requests, drivers, self.currentTime)
                # ******* end match********

                self.requests = remainingRequests

                for (req, driver) in mappings:
                    req['matchedDate'] = self.currentTime
                    driverIdx = int(driver['userId'])
                    self.drivers[driverIdx].updateRoute()
                    self.drivers[driverIdx].matchedRide += 1

                # calc stat
                numOfOccupiedSeat = 0
                numOfCurrentTotalSeats = 0
                numOfSharedOngoingRide = 0
                numOfNonSharedOngoingRide = 0

                for driver in self.drivers:
                    ongoingRideLen = len(driver.driver['ongoingRide'])
                    if ongoingRideLen == 2:
                        numOfSharedOngoingRide += ongoingRideLen
                    if ongoingRideLen == 1:
                        numOfNonSharedOngoingRide += ongoingRideLen

                    numOfOccupiedSeat += len(driver.driver['ongoingRide'])
                    numOfCurrentTotalSeats += self.capacity
                
                # numOfEmptySeats = numOfCurrentTotalSeats - numOfOccupiedSeat
                if numOfCurrentTotalSeats > 0:
                    u = numOfOccupiedSeat / numOfCurrentTotalSeats
                    self.seatUtilization.append( (self.currentTime, u) )
                
                self.numOfRemainingRequests.append( (self.currentTime, len(remainingRequests)) )

                totalOngoingRide = numOfSharedOngoingRide + numOfNonSharedOngoingRide
                if totalOngoingRide > 0:
                    sharedRate = numOfSharedOngoingRide / totalOngoingRide
                    self.shareRates.append( (self.currentTime, sharedRate) )

                numOfMatchedReq = numOfRequest-len(remainingRequests)
                matchRate = numOfMatchedReq / numOfRequest
                if numOfRequest>0:
                    self.matchingRates.append( (self.currentTime, matchRate) )

                if len(mappings)>0:
                    print("[t=%d] match rate=%.3f, matched/unmatched/finished/total requests: %d/%d/%d/%d" % \
                        (self.currentTime, matchRate, len(mappings), len(remainingRequests),len(self.finishedRequests), self.totalRequestCount))
                    
                else:
                    print("[t=%d] No match found. "%(self.currentTime))
                    print("\tmatch rate=%.3f, matched/unmatched/ongoing/finished/total requests: %d/%d/%d/%d" % \
                        (matchRate, len(mappings), len(remainingRequests), len(self.finishedRequests), self.totalRequestCount))
            
            # increment time
            self.currentTime += 1
        
            # move all drivers
            for d in self.drivers:
                d.move(self.currentTime, self.driverSpeed, self.showDetails)

            # detect if all ongoing ride ended
            if self.currentTime >= len(self.requetSeq):
                hasOngoingRideInProgress = False
                for driver in self.drivers:
                    if len(driver.driver['ongoingRide']) > 0:
                        hasOngoingRideInProgress = True
                if not hasOngoingRideInProgress:
                    break
        
        print('[t=%d] Finished all rides'%(self.currentTime))
        print('Num of finished/unmatched/total requests: %d/%d/%d' % (len(self.finishedRequests), len(self.requests), self.totalRequestCount))

        totalWaitingTime = 0
        totalDelay = 0
        # calculate total delay and waiting time
        for req in self.finishedRequests:
            totalWaitingTime += req['startedRideDate'] - req['requestedDate']

            optimalTravelTime = gridWorldDistance(req['startLocation'], req['endLocation']) / self.driverSpeed
            actualTravelTime = req['finishedDate'] - req['requestedDate']
            totalDelay += actualTravelTime - optimalTravelTime
        
        # for req in self.requests:
        #     totalWaitingTime += self.currentTime - req['requestedDate']
        #     totalDelay += self.currentTime - req['requestedDate']

        # print('Total waiting time   = %d'%(totalWaitingTime))
        # print('Total delay          = %d'%(totalDelay))
        reqLen = len(self.finishedRequests) 
        # reqLen = len(self.finishedRequests) + len(self.requests)
        
        self.avgWaitingTime = totalWaitingTime/reqLen
        self.avgtotalDelay = totalDelay/reqLen
        print('Average waiting time = %.3f'%(self.avgWaitingTime))
        print('Average total delay = %.3f'%(self.avgtotalDelay))

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
        self.matchedRide = 0

    def getDriver(self):
        return self.driver
    
    def checkLocation(self, currentTime, showDetails=False):
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
        
        if len(self.route)==0:
            self.updateRoute()

    def move(self, currentTime, speed, showDetails=False):
        self.checkLocation(currentTime)

        # move
        if len(self.driver['ongoingRide'])==0:
            remainingDis = speed
            while remainingDis>0:
                # move random direction
                (x, y) = self.driver['location']
                possibleMoves = [ 
                    (x+min(self.gridWorldW-x, remainingDis), y), 
                    (x-min(x-0, remainingDis), y), 
                    (x, y+min(self.gridWorldH-y, remainingDis)), 
                    (x, y-min(y-0, remainingDis))
                ]
                possibleMoves = [ move for move in possibleMoves 
                    if move[0]>=0 and move[0]<self.gridWorldW 
                        and move[1]>=0 and move[1]<self.gridWorldH
                        and gridWorldDistance(move, (x,y))>0
                ]
                newLoc = possibleMoves[randint(0, len(possibleMoves)-1)]
                self.driver['location'] = newLoc
                remainingDis -= gridWorldDistance((x,y), newLoc)
        else:
            remainingDis = speed
            
            if len(self.route)==0:
                self.updateRoute()

            # move to next point in route
            while remainingDis>0 and len(self.route)>0:
                (x_,y_) = self.route[0]
                (x,y) = self.driver['location']
                # always try to align x axis first
                if randint(0,1)==0:
                    if x < x_:
                        shif = min( remainingDis, x_-x)
                        self.driver['location'] = ( x+shif, y)
                    else:
                        shif = min(remainingDis, x-x_)
                        self.driver['location'] = ( x-shif , y)
                else:
                    if y < y_:
                        shif = min(remainingDis, y_-y)
                        self.driver['location'] = (x, y+shif )
                    else:
                        shif = min(remainingDis, y-y_)
                        self.driver['location'] = (x, y-shif)
                movedDis = gridWorldDistance(self.driver['location'], (x,y))
                remainingDis -= movedDis
                self.checkLocation(currentTime)

                

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
    reqId = 0

    for i in range(numOfSeq):
        requests = []
        startPoints = set()
        endPoints = set()
        # numOfRequests = randint(0, maxNumOfRequestsPerSeq)
        numOfRequests = maxNumOfRequestsPerSeq

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

maxMatchDistance_ = 1000
maxCost_ = 1000

def benchmark(numOfReqToGenAtFirst):
    '''
    Waiting time= T_pickup - T_request
    total travel delay = T_drop - T*_arrive
        where T*_arrive the earliest possible time at which the destination could be reached
    
    1 time unit ~ 6 seconds
    1 space unit ~ 1 meter
    '''
    gridWorldH = 1000  # 1km
    gridWorldW = 5000  # 5km 
    totalRequests = numOfReqToGenAtFirst
    numOfDriversChoices = [
        (numOfReqToGenAtFirst)//2,   
        (numOfReqToGenAtFirst)//4,  
        (numOfReqToGenAtFirst)//6,  
    ]

    greedySimulators = []
    dynamicSimulators = []

    for numOfDrivers in numOfDriversChoices:

        # generate requets for all rounds
        requetSeq = generateRequetSeq(gridWorldW, gridWorldH, 1, numOfReqToGenAtFirst)

        # generate driver locations
        driverLocSeq = []
        for i in range(1):
            dn = numOfDrivers
            driversLoc = []
            for _ in range(dn):
                x = randint(0, gridWorldW-1)
                y = randint(0, gridWorldH-1)
                driversLoc.append( (x,y) )
            driverLocSeq.append( driversLoc )

        # print stats

        totalRequest = 0
        for seq in requetSeq:
            totalRequest += len(seq)

        print()
        print('num of requsts =', totalRequest)
        print('num of drivers =', numOfDrivers)

        print()
        print('Start Greedy simulation')
        gridWorld_greedy = GridWorldSimulator(
            gridWorldW=gridWorldW,
            gridWorldH=gridWorldH,
            constraints_param={ 
                'maxMatchDistance': maxMatchDistance_,
            }, 
            requetSeq=requetSeq,
            driverLocSeq=driverLocSeq,
            driverSpeed=82,    # ~25 km/h
            capacity=2,
            matchEngineTriggerInterval=10,
            algo='greedy',
            showDetails=False
        )
        gridWorld_greedy.startSimulator(benchmark=True)

        print()
        print('Start Dynamic simulation')
        gridWorld_dynamic = GridWorldSimulator(
            gridWorldW=gridWorldW,
            gridWorldH=gridWorldH,
            constraints_param={ 
                'maxMatchDistance': maxMatchDistance_,
                'maxCost': maxCost_
            }, 
            requetSeq=requetSeq,
            driverLocSeq=driverLocSeq,
            driverSpeed=82,    # ~50 km/h
            capacity=2,
            matchEngineTriggerInterval=10,
            algo='dynamic',
            showDetails=False
        )
        gridWorld_dynamic.startSimulator(benchmark=True)

        print()
        # calculate avg travel distance of requests
        startLocations = [ req['startLocation'] for seq in requetSeq for req in seq ]
        endLocations = [ req['endLocation'] for seq in requetSeq for req in seq ]
        avgTravelDis = 0
        for (s1, s2) in zip(startLocations, endLocations):
            avgTravelDis += gridWorldDistance(s1, s2)
        avgTravelDis /= len(driverLocSeq)
        print('Average travel distance of request:', avgTravelDis)

        # calculate avg distance of pairwise drivers' initial locations
        driversLocations = [  loc for seq in driverLocSeq for loc in seq ]
        driverInitLocationPairs = list(combinations(driversLocations, 2))
        locationAvgDistance = 0
        for (s1, s2) in driverInitLocationPairs:
            locationAvgDistance += gridWorldDistance(s1, s2)
        locationAvgDistance /= len(driverInitLocationPairs)
        print('Average distance of pairwise drivers\' locations:', locationAvgDistance)

        greedySimulators.append(gridWorld_greedy)
        dynamicSimulators.append(gridWorld_dynamic)


    labels = ('1:2\n(%d:%d)'%(totalRequests//2, totalRequests), 
        '1:4\n(%d:%d)'%(totalRequests//4, totalRequests), 
        '1:6\n(%d:%d)'%(totalRequests//6, totalRequests),)

    # plot figure
    gs = gridspec.GridSpec(1, 2)

    ax = plt.subplot(gs[0, 0])
    numOfBarGroup = 3
    idex = np.arange(numOfBarGroup)
    bar_width = 0.35
    opacity = 0.8
    data_1 = tuple([ len(sim.requests) for sim in greedySimulators])
    data_2 = tuple([ len(sim.requests) for sim in dynamicSimulators])
    rects1 = ax.bar(idex, data_1, bar_width, alpha=opacity, color='c', label='Greedy')
    rects2 = ax.bar(idex + bar_width, data_2, bar_width, alpha=opacity, color='y', label='Dynamic')
    ax.set_ylabel('# of requests', fontsize=18)
    ax.set_title('Unhandled Requests', fontsize=20)
    ax.set_xticks(idex + bar_width/2)
    ax.set_xticklabels( labels , fontsize=18
    )
    ax.legend()

    ax = plt.subplot(gs[0, 1])
    numOfBarGroup = 3
    idex = np.arange(numOfBarGroup)
    bar_width = 0.35
    opacity = 0.8
    data_1 = tuple([ sim.avgtotalDelay for sim in greedySimulators])
    data_2 = tuple([ sim.avgtotalDelay for sim in dynamicSimulators])
    rects1 = ax.bar(idex, data_1, bar_width, alpha=opacity, color='r', label='Greedy')
    rects2 = ax.bar(idex + bar_width, data_2, bar_width, alpha=opacity, color='b', label='Dynamic')
    ax.set_ylabel('time unit', fontsize=16)
    ax.set_title('Total Delay', fontsize=20)
    ax.set_xticks(idex + bar_width/2)
    ax.set_xticklabels( labels, fontsize=18
    )
    ax.legend()

    fig = plt.gcf()
    fig.set_size_inches(24, 12)
    fig.suptitle('Performance of different driver-request ratio', fontsize=26)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fig.savefig('simulationResult/%s_benchmark_%drequest_.png'%(timestr, totalRequests))
    fig.clear()

def peakTrafficTime(unitOfTimeToGenerate, maxNumOfReqGeneratePerUnitTime, totalDriver):
    '''
    Waiting time= T_pickup - T_request
    total travel delay = T_drop - T*_arrive
        where T*_arrive the earliest possible time at which the destination could be reached
    
    1 time unit ~ 6 seconds
    1 space unit ~ 1 meter
    '''
    gridWorldH = 1000  # 1km
    gridWorldW = 5000  # 5km
    totalRequests = unitOfTimeToGenerate*maxNumOfReqGeneratePerUnitTime
    numOfDriversChoices = [
        totalDriver,   
        # totalRequests//20,   
        # totalRequests//30,  
    ]

    for numOfDrivers in numOfDriversChoices:

        # generate requets for all rounds
        requetSeq = generateRequetSeq(gridWorldW, gridWorldH, unitOfTimeToGenerate, maxNumOfReqGeneratePerUnitTime)

        # generate driver locations
        driverLocSeq = []
        for i in range(unitOfTimeToGenerate):
            if i==0:
                dn = numOfDrivers
                driversLoc = []
                for _ in range(dn):
                    x = randint(0, gridWorldW-1)
                    y = randint(0, gridWorldH-1)
                    driversLoc.append( (x,y) )
                driverLocSeq.append( driversLoc )
            else:
                driverLocSeq.append( [] )

        # print stats

        totalRequest = totalRequests

        print()
        print('num of requsts =', totalRequest)
        print('num of drivers =', numOfDrivers)

        print()
        # calculate avg travel distance of requests
        startLocations = [ req['startLocation'] for seq in requetSeq for req in seq ]
        endLocations = [ req['endLocation'] for seq in requetSeq for req in seq ]
        avgTravelDis = 0
        for (s1, s2) in zip(startLocations, endLocations):
            avgTravelDis += gridWorldDistance(s1, s2)
        avgTravelDis /= len(driverLocSeq)
        print('Average travel distance of request:', avgTravelDis)

        # calculate avg distance of pairwise drivers' initial locations
        driversLocations = [  loc for seq in driverLocSeq for loc in seq ]
        driverInitLocationPairs = list(combinations(driversLocations, 2))
        locationAvgDistance = 0
        for (s1, s2) in driverInitLocationPairs:
            locationAvgDistance += gridWorldDistance(s1, s2)
        locationAvgDistance /= len(driverInitLocationPairs)
        print('Average distance of pairwise drivers\' locations:', locationAvgDistance)

        print()
        print('Start Greedy simulation')
        gridWorld_greedy = GridWorldSimulator(
            gridWorldW=gridWorldW,
            gridWorldH=gridWorldH,
            constraints_param={ 
                'maxMatchDistance': maxMatchDistance_,
            }, 
            requetSeq=requetSeq,
            driverLocSeq=driverLocSeq,
            driverSpeed=82,    # ~25 km/h
            capacity=2,
            matchEngineTriggerInterval=10,
            algo='greedy',
            showDetails=False
        )
        gridWorld_greedy.startSimulator()

        print()
        print('Start Dynamic simulation')
        gridWorld_dynamic = GridWorldSimulator(
            gridWorldW=gridWorldW,
            gridWorldH=gridWorldH,
            constraints_param={ 
                'maxMatchDistance': maxMatchDistance_,
                'maxCost': maxCost_
            }, 
            requetSeq=requetSeq,
            driverLocSeq=driverLocSeq,
            driverSpeed=82,    # ~50 km/h
            capacity=2,
            matchEngineTriggerInterval=10,
            algo='dynamic',
            showDetails=False
        )
        gridWorld_dynamic.startSimulator()

        # plot figure
        gs = gridspec.GridSpec(2, 2)

        ax = plt.subplot(gs[0, 0])
        ax.set_title('Matching Rate', fontsize=20)
        ax.set_xlabel('time', fontsize=18)
        ax.set_ylabel('# of matched requests / # of total requests', fontsize=12)
        x = [ x for (x, _) in gridWorld_greedy.matchingRates ]
        y = [ y for (_, y) in gridWorld_greedy.matchingRates ]
        ax.plot(x, y, linestyle='-', label='greedy')
        x = [ x for (x, _) in gridWorld_dynamic.matchingRates ]
        y = [ y for (_, y) in gridWorld_dynamic.matchingRates ]
        ax.plot(x, y, linestyle='--', label='dynamic')
        ax.legend()

        ax = plt.subplot(gs[0, 1])
        ax.set_title('Ride Share Rate', fontsize=20)
        ax.set_xlabel('time', fontsize=18)
        ax.set_ylabel('# of rides that share car with others / # of total rides', fontsize=12)
        x = [ x for (x, _) in gridWorld_greedy.shareRates ]
        y = [ y for (_, y) in gridWorld_greedy.shareRates ]
        ax.plot(x, y, linestyle='-', label='greedy')
        x = [ x for (x, _) in gridWorld_dynamic.shareRates ]
        y = [ y for (_, y) in gridWorld_dynamic.shareRates ]
        ax.plot(x, y, linestyle='--', label='dynamic')
        ax.legend()

        ax = plt.subplot(gs[1, 0])
        ax.set_title('Accumulated unhandled requets', fontsize=20)
        ax.set_xlabel('time', fontsize=18)
        ax.set_ylabel('# of unhandled requets', fontsize=18)
        x = [ x for (x, _) in gridWorld_greedy.numOfRemainingRequests ]
        y = [ y for (_, y) in gridWorld_greedy.numOfRemainingRequests ]
        ax.plot(x, y, linestyle='-', label='greedy')
        x = [ x for (x, _) in gridWorld_dynamic.numOfRemainingRequests ]
        y = [ y for (_, y) in gridWorld_dynamic.numOfRemainingRequests ]
        ax.plot(x, y, linestyle='--', label='dynamic')
        ax.legend()

        ax = plt.subplot(gs[1, 1])
        numOfBarGroup = 2
        idex = np.arange(numOfBarGroup)
        bar_width = 0.35
        opacity = 0.8
        greedy_data = (gridWorld_greedy.avgWaitingTime, gridWorld_greedy.avgtotalDelay)
        dynamic_data = (gridWorld_dynamic.avgWaitingTime, gridWorld_dynamic.avgtotalDelay)
        rects1 = ax.bar(idex, greedy_data, bar_width, alpha=opacity, color='r', label='Greedy')
        rects2 = ax.bar(idex + bar_width, dynamic_data, bar_width, alpha=opacity, color='b', label='Dynamic')
        ax.set_ylabel('time unit', fontsize=18)
        ax.set_title('Delay', fontsize=20)
        ax.set_xticks(idex + bar_width/2)
        ax.set_xticklabels( ('avg waiting time', 'avg total delay'), fontsize=14)
        ax.legend()

        fig = plt.gcf()
        fig.set_size_inches(15, 12)
        fig.suptitle('%d fix drivers / %d total ride requests'%(numOfDrivers, totalRequest), fontsize=26)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        fig.savefig('simulationResult/%s_peak_%d_%d.png'%(timestr, numOfDrivers, totalRequest))

if __name__ == '__main__':
    peakTrafficTime(200, 5, 100)
    #benchmark(100)