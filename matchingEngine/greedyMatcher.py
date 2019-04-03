from itertools import permutations

import googleMapApiAdapter as gMapApi
import univLoc
from utils import haversineDistance

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
    Q <- all requests, D <- all drivers, R <- {}, M <- {}
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
        self.useGridWorld = useGridWorld

    def _getDistanceMatrix(self, origins, destinations):
        if self.useGridWorld:
            # TODO
            return None
        else:
            return gMapApi.getDistanceMatrix(origins, destinations)

    def match(self, requests, drivers):
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
            "capacity": number           }]
        
        output
        (M, R) format:
        ( [{request, driver}], [request] )

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

        possibleMappings.sort()
        matchedRquestIDs = set()

        for cost, r, d in possibleMappings:
            if r['id'] in matchedRquestIDs or (not self._isSatisfyConstraints(r,d)):
                continue
            
            r['estimatedWaitingCost'] = cost
            d['ongoingRide'].append(r)
            mappings.append( (r,d) )
            matchedRquestIDs.add(r['id'])
        
        remainingRequests = [ r for r in requests if r['id'] not in matchedRquestIDs ]
        return (mappings, remainingRequests)

    def _isSatisfyConstraints(self, request, driver):
        '''
        1. driver.capacity > 0
        2. dist(driver.currentLocation, request.startLocation) <= maxMatchDistance
        3. there is already passenger(s) in car ->  check if the total length of the best shared route would be longer than the sum of the single routes
        '''
        if driver['capacity'] <= len(driver['ongoingRide']):
            return False
        
        if haversineDistance(request['startLocation'], driver['location']) > self.maxMatchDistance:
            return False

        if len(driver['ongoingRide']) > 0:
            # at least one ongoign ride is sharable with current request
            for onGoingRide in driver['ongoingRide']:
                if self._isShareable(driver['location'], request, onGoingRide):
                    return True
            return False
        
        # not violating any constraint
        return True
    
    def _isShareable(self, driverLoc, requestToMatch, onGoingRide):
        print('requestToMatch', requestToMatch)
        s1 = requestToMatch['startLocation']
        t1 = requestToMatch['endLocation']
        s2 = onGoingRide['startLocation']
        t2 = onGoingRide['endLocation']
        if onGoingRide['isOnCar']:
            origins = [s1, t1, t2, driverLoc]
            destinations = [s1, t1, t2]
            n = 3
        else:
            origins = [s1, t1, s2, t2, driverLoc]
            destinations = [s1, t1, s2, t2]
            n = 4
        
        distMatrix = self._getDistanceMatrix(origins, destinations)
        print('distMatrix', distMatrix)
        
        # calculate the cost fo all possible routes
        allCostPathTuples = []
        for path in permutations(list(range(n))):
            cost = distMatrix[n][path[0]]
            for i in range(n-1):
                cost += distMatrix[ path[i] ][ path[i+1] ]
            allCostPathTuples.append( (cost, path) )
        
        print('allCostPathTuples', allCostPathTuples)
    
        (bestRouteCost, bestRoutePath) = min(allCostPathTuples)
        
        if onGoingRide['isOnCar']:
            sumOfSingleRouteCost = distMatrix[0][1] + distMatrix[3][2]
        else:
            sumOfSingleRouteCost = distMatrix[0][1] + distMatrix[1][2] + distMatrix[2][3] + distMatrix[3][bestRoutePath[0]]

        print(bestRouteCost, sumOfSingleRouteCost)
        return bestRouteCost <= sumOfSingleRouteCost

        
    

def greedyMatcherTest():

    requests = [
        {
            "id": '1',
            "userId": 'Eric',
            "startLocation": univLoc.hku,
            "endLocation": univLoc.cu,
            "timestamp": 1553701200965
        },
        {
            "id": '2',
            "userId": 'Tony',
            "startLocation": univLoc.cu,
            "endLocation": univLoc.hku,
            "timestamp": 1553701760965
        }
    ]

    onGoingReq1 = {
        "id": '3',
        "userId": 'David',
        "startLocation": univLoc.cu,
        "endLocation": univLoc.hku,
        "timestamp": 1553701060965,
        "isOnCar": False
    }

    drivers = [
        {
            "userId": 'Antony',
            "location":  univLoc.cu,
            "ongoingRide": [onGoingReq1],
            "capacity": 4
        },
        {
            "userId": 'Elven',
            "location":  univLoc.polyu,
            "ongoingRide": [],
            "capacity": 4
        }
    ]

    gMatcher = GreedyMatcher({ 'maxMatchDistance': 1 })
    M, R = gMatcher.match(requests, drivers)
    print('mapping (passenger->driver): ')
    for q, d in M:
        print("  %s -> %s" %(q['userId'], d['userId']))
    print('remaining requests: ', len(R))

if __name__ == "__main__":
    greedyMatcherTest()