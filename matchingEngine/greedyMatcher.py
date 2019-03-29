import googleMapApiAdapter as gMapApi
import univLoc
from utils import haversineDistance, isShareable

class GreedyMatcher:
    '''
    A simple greedy algorithm for real time ride matching executed in every time frame
    
    Input: a set of requests Q, a set of drivers D
    Output: a set of unhandled requests R, a set of mapping M
    
    Steps:
    1. Q <- all requests, D <- all drivers, R <- {}, M <- {}
    2. for each q ∈ Q:
    3.      S <- { d ∈ D | d satistfy constraints Z regarding q }
    4.      if isEmpty(S):
    5.          R.add(q)
    6.          continue loop
    7.      u <- argmin s ∈ S ( distance(s.current_location, q.start_location) )
    8.      u.emptySeat <- u.emptySeat - 1
    9.      M.add( (q,u) )
   10. return M, R
    '''
    def __init__(self, constraints_param):
        '''
        constraints_param format:
        {
            # max distance between driver's location and request's start point allowed to be matched
            "maxMatchDistance": number    
        }
        '''
        self.maxMatchDistance = constraints_param['maxMatchDistance']

    def match(self, requests, drivers):
        '''
        Input
        requests format:
        [{  "userId": string,
            "startLocation": {
                "latitude": number,
                "longitude": number
            },
            "endLocation": {
                "latitude": number,
                "longitude": number
            }
            "timestamp": number         }]
        drivers format:
        [{  "userId": string,
            "location":  {
                "latitude": number,
                "longitude": number
            },
            "ongoingRide": [ requests ],
            "maxSeat": number           }]
        
        output
        (M, R) format:
        ( [{request, driver}], [request] )

        '''
        if(len(requests)==0 or len(drivers)==0):
            return ([], requests)

        remainingRequests = []
        mappings = []

        requests_startLocations = [ request['startLocation'] for request in requests ]
        drivers_locations = [ driver['location'] for driver in drivers ]
        distMatrix = gMapApi.getDistanceMatrix(requests_startLocations, drivers_locations)

        for (request, dist) in zip(requests, distMatrix):
            # dist = [ (distance in km, duration in seconds) ]
            candidatesDistTuple = [ 
                (driver, d[0]) for (driver, d) in zip(drivers, dist) if self.isSatisfyConstraints(request, driver) 
            ]
            
            if len(candidatesDistTuple)==0:
                remainingRequests.append(request)
                continue
            
            # find driver index with min dist
            minDist = candidatesDistTuple[0][1]
            nearestCandidateIdx = 0
            for i in range(1, len(candidatesDistTuple)):
                if(candidatesDistTuple[i][1] < minDist):
                    minDist = candidatesDistTuple[i][1]
                    nearestCandidateIdx = i
            
            mappings.append( (request, candidatesDistTuple[nearestCandidateIdx][0]) )
            candidatesDistTuple[nearestCandidateIdx][0]['ongoingRide'].append(request)

        return (mappings, remainingRequests)
            

    def isSatisfyConstraints(self, request, driver):
        '''
        1. driver.emptySeat > 0
        2. dist(driver.currentLocation, request.startLocation) <= maxMatchDistance
        3. there is already passenger(s) in car -> at least one ongoing request in car that is sharable with the request being match. (two requests are shareable if the distance of best shared route < sum of the individual trip distances)
        '''
        if driver['maxSeat'] <= len(driver['ongoingRide']):
            return False
        
        if haversineDistance(request['startLocation'], driver['location']) > self.maxMatchDistance:
            return False

        # if len(driver['ongoingRide']) > 0:
        #     onGoingReqs = [ (l['startLocation'], l['endLocation']) for l in driver['ongoingRide'] ]
        #     for onGoingReq in onGoingReqs:
        #         if isShareable(request['startLocation'], request['endLocation'], onGoingReq[0], onGoingReq[1]):
        #             return True
        #     return False
        
        # not violating any constraint
        return True


def greedyMatcherTest():

    requests = [
        {
            "userId": 'Eric',
            "startLocation": univLoc.hku,
            "endLocation": univLoc.cu,
            'timestamp': 1553701200965
        },
        {
            "userId": 'Tony',
            "startLocation": univLoc.cu,
            "endLocation": univLoc.hku,
            'timestamp': 1553701760965
        }
    ]

    drivers = [
        {
            "userId": 'Antony',
            "location":  univLoc.cu,
            "ongoingRide": [],
            "maxSeat": 4
        },
        {
            "userId": 'Elven',
            "location":  univLoc.polyu,
            "ongoingRide": [],
            "maxSeat": 4
        }
    ]

    gMatcher = GreedyMatcher({ 'maxMatchDistance': 2 })
    M, R = gMatcher.match(requests, drivers)
    print('mapping (passenger->driver): ')
    for q, d in M:
        print("  %s -> %s" %(q['userId'], d['userId']))
    print('remaining requests: ', len(R))

if __name__ == "__main__":
    greedyMatcherTest()