from itertools import permutations

import googleMapApiAdapter as gMapApi
from loc import loc
from utils import haversineDistance, gridWorldDistance ,gridWorldDistanceMatrix

class GreedyMatcher:
    '''
    A simple greedy algorithm for real time ride matching executed in every time frame
    
    Input: 
        Q: a set of requests
        D: a set of drivers
    Output: 
        R: a set of remaining requests
        M: a set of mapping
    
    Steps:
    Q <- all requests, D <- all drivers, M <- {}
    C <- { (q, d ) | q ∈ Q ∧ d ∈ D }
    sort C in ascending order by distance(q.start_location, s.current_location)
    S <- {}
    for each c ∈ C:
        (cost, q, d) <- c
        if (q ∉ S) AND (q and d satistfy constraints Z):
            M.add( (q,d) )
            S.add( q )
    R <- { q | q ∈ Q ∧ q ∉ S }
    return M, R
    '''
    def __init__(self, constraints_param, useGridWorld=False):
        '''
        constraints_param format:
        {
            # max distance between driver's location and request's start point allowed to be matched
            "maxMatchDistance": number    
        }
        '''
        self.maxMatchDistance = constraints_param['maxMatchDistance']
        if 'maxWaitingTime' in constraints_param:
            self.maxWaitingTime = constraints_param['maxWaitingTime']
        else:
            self.maxWaitingTime = None
        self.useGridWorld = useGridWorld

    def _getDistanceMatrix(self, origins, destinations):
        if self.useGridWorld:
            return gridWorldDistanceMatrix(origins, destinations)
        else:
            return gMapApi.getDistanceMatrix(origins, destinations)
    
    def _getStrictLineDistance(self, origin, destination):
        if self.useGridWorld:
            return gridWorldDistance(origin, destination)
        else:
            return haversineDistance(origin, destination)

    def match(self, requests, drivers, currentTime=None):
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
            "timestamp": number,
            "isOnCar": False,
        ]
        drivers format:
        [{  "userId": string,
            "location":  {
                "latitude": number,
                "longitude": number
            },
            "ongoingRide": [ requests ],
            "capacity": number,
            "timestamp": number           }]
        
        output
        (M, R) format:
        ( [(request, driver)], [request] )

        '''
        if(len(requests)==0 or len(drivers)==0):
            return ([], requests)

        mappings = []
        requests_startLocations = [ request['startLocation'] for request in requests ]
        drivers_locations = [ driver['location'] for driver in drivers ]
        distMatrix = self._getDistanceMatrix(drivers_locations, requests_startLocations)

        possibleMappings = []  # ( distance, request, driver)
        for i in range(len(drivers)):
            for j in range(len(requests)):
                mapping = (distMatrix[i][j], requests[j], drivers[i])
                possibleMappings.append(mapping)

        possibleMappings.sort(key=lambda x: x[0])
        matchedRquestIDs = set()

        for cost, r, d in possibleMappings:
            if r['id'] in matchedRquestIDs or (not self._isSatisfyConstraints(r, d, currentTime)):
                continue
            
            r['estimatedWaitingCost'] = cost
            d['ongoingRide'].append(r)
            mappings.append( (r,d) )
            matchedRquestIDs.add(r['id'])
        
        remainingRequests = [ r for r in requests if r['id'] not in matchedRquestIDs ]
        return (mappings, remainingRequests)

    def _isSatisfyConstraints(self, request, driver, currentTime=None):
        '''
        1. driver.capacity > 0
        2. dist(driver.currentLocation, request.startLocation) <= maxMatchDistance
        3. there is already passenger(s) in car ->  check if the total length of the best shared route would be longer than the sum of the single routes
        '''
        if driver['capacity'] <= len(driver['ongoingRide']):
            return False
        
        if self._getStrictLineDistance(request['startLocation'], driver['location']) > self.maxMatchDistance:
            # if currentTime!=None and self.maxWaitingTime!=None and currentTime - request['requestedDate'] > self.maxWaitingTime:
            #     return True
            # else:
            #     return False
            return False

        if len(driver['ongoingRide']) > 0:
            return self._isShareable(driver['location'], request, driver['ongoingRide'])
        
        # not violating any constraint
        return True
    
    def _isShareable(self, driverLoc, requestToMatch, onGoingRides):
        '''
        origins = [ onGoingRides start and end , requestToMatch start and end , driverLoc ]
        destinations = [ onGoingRides start and end , requestToMatch start and end ]
        '''
        origins = []
        destinations = []
        for onGoingRide in onGoingRides:

            if 'isOnCar' not in onGoingRide:
                onGoingRide['isOnCar'] = False

            if onGoingRide['isOnCar']:
                # only consider endLocation
                end = onGoingRide['endLocation']
                origins.append(end)
                destinations.append(end)
            else:
                start = onGoingRide['startLocation']
                end = onGoingRide['endLocation']
                origins.append(start)
                origins.append(end)
                destinations.append(start)
                destinations.append(end)
        s1 = requestToMatch['startLocation']
        t1 = requestToMatch['endLocation']
        origins.append(s1)
        origins.append(t1)
        destinations.append(s1)
        destinations.append(t1)
        numOfReqLocations = len(destinations)
        origins.append(driverLoc)
        
        distMatrix = self._getDistanceMatrix(origins, destinations)
        
        # calculate the cost fo all possible routes
        possible_cost_bestRoutes = []
        pathLen = numOfReqLocations
        for path in permutations(list(range(pathLen))):
            cost = distMatrix[-1][path[0]]
            for i in range(pathLen-1):
                cost += distMatrix[ path[i] ][ path[i+1] ]
            possible_cost_bestRoutes.append( (cost, path) )
        
        # print('possible_cost_bestRoutes', possible_cost_bestRoutes)
    
        (bestRouteCost, bestRoutePath) = min(possible_cost_bestRoutes)
        # print(bestRoutePath)
        

        # # calculate best route of onGoingRides
        # possible_cost_bestOnGoingRoutes = []
        # pathLen = numOfReqLocations-2
        # for path in permutations(list(range(pathLen))):
        #     cost = distMatrix[-1][path[0]]
        #     for i in range(pathLen-1):
        #         cost += distMatrix[ path[i] ][ path[i+1] ]
        #     possible_cost_bestOnGoingRoutes.append( (cost, path) )
        
        # # print('possible_cost_bestOnGoingRoutes', possible_cost_bestOnGoingRoutes)
    
        # (bestOnGoingRouteCost, bestOnGoingRoutePath) = min(possible_cost_bestOnGoingRoutes)

        # # distance(requestToMatch) + distance(bestOnGoingRoute)
        # sumOfSeperateCost = bestOnGoingRouteCost + distMatrix[numOfReqLocations-2][numOfReqLocations-1]
        
        sumOfSeperateCost = 0
        i = 0
        for ongoing in onGoingRides:
            if ongoing['isOnCar']:
                sumOfSeperateCost += distMatrix[-1][i+1]
            else:
                sumOfSeperateCost += distMatrix[i][i+1]
            i+=2
        sumOfSeperateCost += distMatrix[-3][-2]

        print(bestRouteCost, sumOfSeperateCost)
        return bestRouteCost <= sumOfSeperateCost

        
def greedyMatcherTest1():
    requests = [
        {
            "id": '1',
            "userId": 'R1',
            "startLocation": loc['cityu'],
            "endLocation": loc['mk_station'],
            "timestamp": 1553701760965,
            "isOnCar": False
        }
    ]

    drivers = [
        {
            "userId": 'D1',
            "location":  loc['kowloon_tong_station'],
            "ongoingRide": [],
            "capacity": 4
        },
        {
            "userId": 'D2',
            "location":  loc['mk_station'],
            "ongoingRide": [],
            "capacity": 4
        }
    ]

    gMatcher = GreedyMatcher({ 'maxMatchDistance': 5000 })
    M, R = gMatcher.match(requests, drivers)
    print('mapping (passenger->driver): ')
    for q, d in M:
        print("  %s -> %s" %(q['userId'], d['userId']))
    print('remaining requests: ', len(R))


def greedyMatcherTest2():

    requests = [
        {
            "id": '1',
            "userId": 'R1',
            "startLocation": loc['cu'],
            "endLocation": loc['sai_ying_pun_station'],
            "timestamp": 1553701760965,
            "isOnCar": False
        },
        {
            "id": '2',
            "userId": 'R2',
            "startLocation": loc['city_one'],
            "endLocation": loc['ust'],
            "timestamp": 1553701760965,
            "isOnCar": False
        },
        {
            "id": '3',
            "userId": 'R3',
            "startLocation": loc['city_one'],
            "endLocation": loc['sha_tin'],
            "timestamp": 1553701760965,
            "isOnCar": False
        },
        {
            "id": '4',
            "userId": 'R4',
            "startLocation": loc['mk_station'],
            "endLocation": loc['ust'],
            "timestamp": 1553701760965,
            "isOnCar": False
        }
    ]

    onGoingReq1 = {
        "id": '4',
        "userId": 'OR1',
        "startLocation": loc['science_park'],
        "endLocation": loc['hku'],
        "timestamp": 1553701060965,
        "isOnCar": True
    }

    onGoingReq2 ={
        "id": '5',
        "userId": 'OR2',
        "startLocation": loc['science_park'],
        "endLocation": loc['cu'],
        "timestamp": 1553701200965,
        "isOnCar": True
    }


    drivers = [
        {
            "userId": 'D1',
            "location":  loc['racecourse_station'],
            "ongoingRide": [onGoingReq1, onGoingReq2],
            "capacity": 4
        },
        {
            "userId": 'D2',
            "location":  loc['polyu'],
            "ongoingRide": [],
            "capacity": 4
        }
    ]

    gMatcher = GreedyMatcher({ 'maxMatchDistance': 5000 })
    M, R = gMatcher.match(requests, drivers)
    print('mapping (passenger->driver): ')
    for q, d in M:
        print("  %s -> %s" %(q['userId'], d['userId']))
    print('remaining requests: ', len(R))

if __name__ == "__main__":
    # greedyMatcherTest1()
    greedyMatcherTest2()