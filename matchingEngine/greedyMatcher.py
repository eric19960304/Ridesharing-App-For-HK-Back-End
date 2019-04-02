import googleMapApiAdapter as gMapApi
import univLoc
from utils import haversineDistance, isShareable

class GreedyMatcher:
    '''
    A simple greedy algorithm for real time ride matching executed in every time frame
    
    Input: 
        Q: a set of requests
        D: a set of drivers
    Output: 
        R: a set of unhandled requests
        M: a set of mapping
    
    Steps:
    Q <- all requests, D <- all drivers, R <- {}, M <- {}
    if |Q| <= |D|:
        for each q ∈ Q:
            S <- { d | d ∈ D , d satistfy constraints Z regarding q }
            u <- argmin<s ∈ S>( distance(s.current_location, q.start_location) )
            u.emptySeat <- u.emptySeat - 1
            M.add( (q,u) )
    else:
        for each d ∈ D:
            S <- { q | q ∈ Q , d satistfy constraints Z regarding q }
            sort S in asc order of distance(d.current_location, s.start_location) ) where s ∈ S
            k = min(|S|, d.emptySeat)
            U <- first k elements in S
            d.emptySeat <- d.emptySeat - k 
            for u ∈ U:
                M.add( (u,d) )
    R <- { q | q ∈ Q , q not in { a | (a,b) ∈ M } }
    return M, R
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
            "timestamp": number,
            "estimatedOptimal": [ 
                "distance": number, 
                "duration": number 
            ]                           }]
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
        print(distMatrix)
        if len(requests) <= len(drivers):

            for (request, dist) in zip(requests, distMatrix):
                # dist = [ (distance in km, duration in seconds) ]
                costDriverTuples = [ 
                    (c[0], driver) for (driver, c) in zip(drivers, dist) 
                        if self.isSatisfyConstraints(request, driver) 
                ]
                costDriverTuples.sort()
                
                driverToMatch = costDriverTuples[0][1]
                mappings.append( (request, driverToMatch) )
                driverToMatch['ongoingRide'].append(request)
        else:
            distMatrix_transposed = list(map(list, zip(*distMatrix)))
            for (driver, dist) in zip(drivers, distMatrix_transposed):
                costRequestTuples = [ 
                    (c[0], request) for (request, c) in zip(requests, dist) 
                        if self.isSatisfyConstraints(request, driver) 
                ]
                costRequestTuples.sort()

                remainingSeats = driver['maxSeat'] - len(driver['ongoingRide'])
                requestsToMatch = [ r for c,r in costRequestTuples[:remainingSeats] ]
                for r in requestsToMatch:
                    mappings.append( (r, driver) )
                    driver['ongoingRide'].append(r)
        
        matchedRequsts = [ r for (r,d) in mappings ]
        remainingRequests = [ r for r in requests if r not in matchedRequsts ]
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