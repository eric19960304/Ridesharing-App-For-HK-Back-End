from random import randint
from greedyMatcher import GreedyMatcher
from utils import gridWorldDistance
from itertools import combinations
from collections import deque
class GridWorldSimulator:
    '''
    requests format:
        [{  
            "id": string,
            "userId": string,
            "startLocation": (int, int),
            "endLocation": (int, int),
            "timestamp": number,
            "isOnCar": False,
        }]
    drivers format:
    [{
        "userId": string,
        "location":  (int, int),
        "ongoingRide": [ requests ],
        "capacity": number,
        "timestamp": number
    }]
    '''

    def __init__(self, gridWorldSize, constraints_param, testingDuration, requestGenDuration, maxNumOfRequestsGenPerRound, numOfDrivers, capacity):
        self.gridWorldSize = gridWorldSize
        self.constraints_param = constraints_param
        self.testingDuration = testingDuration
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

    def _generateRandomRequests(self):
        '''
        return list of points, size is randomized between [1, maxNumOfRequestsGenPerRound-1]
        '''
        startPoints = set()
        endPoints = set()
        numOfRequests = randint(1, self.maxNumOfRequestsGenPerRound)
        for i in range(numOfRequests):
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
                "timestamp": self.currentTime,
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


    def startSimulator(self):

        matcher = GreedyMatcher(self.constraints_param)
        drivers = []

        for i in range(self.numOfDrivers):
            x = randint(0, self.gridWorldSize-1)
            y = randint(0, self.gridWorldSize-1)
            initLoc = (x,y)
            drivers.append( Driver(finishedRequestsRef=self.finishedRequests, \
                userId=i, initialLocation=initLoc, capacity=self.capacity, gridWorldSize=self.gridWorldSize) )

        for currentTime in range(1, self.testingDuration):

            self._generateRandomRequests()
            
            if currentTime%5==0:
                
                requestLen = len(self.requests)
                
                mappings, remainingRequests = matcher.match(self.requests, self.drivers)

                self.requests = remainingRequests

                matchRate = (requestLen-len(remainingRequests))/requestLen
                self.matchingRates.append(matchRate)
                print( "[%d] match rate =  %.3f"%(currentTime, matchRate) )

class Driver:
    def __init__(self, finishedRequestsRef, userId, initialLocation, capacity, gridWorldSize):
        self.finishedRequestsRef = finishedRequestsRef
        self.driver = {
            "userId": str(userId),
            "location":  initialLocation,
            "ongoingRide": [],
            "capacity": capacity,
            "timestamp": 0
        }
        self.route = deque()
        self.gridWorldSize = gridWorldSize
    
    def getDriver(self, currentTime):
        self.driver['timestamp'] = currentTime
        return self.driver
    
    def move(self):
        if len(self.driver['ongoingRide'])==0:
            # move random direction
            (x, y) = self.driver['location']
            possibleMoves = [ (x+1, y), (x-1, y), (x, y+1), (x, y-1) ]
            possibleMoves = [ move for move in possibleMoves 
                if move[0]>=0 and move[0]<self.gridWorldSize and move[1]>=0 and move[1]<self.gridWorldSize
            ]
            newLoc = possibleMoves[randint(0, len(possibleMoves))]


        for ride in self.driver['ongoingRide']:
            if self.driver['location']:
                pass

    def updateRoute(self):
        pass


if __name__ == '__main__':
    gridWorld = GridWorldSimulator(gridWorldSize=100, constraints_param={ 'maxMatchDistance': 10 }, \
        testingDuration=200, requestGenDuration=100, maxNumOfRequestsGenPerRound=7, \
        numOfDrivers=20, capacity=2)
