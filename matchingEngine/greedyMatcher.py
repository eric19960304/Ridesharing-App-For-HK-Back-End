import googleMapApiAdapter as gMapApi
import univLoc

class GreedyMatcher:
    '''
    Executed in every time frame
    
    A simple greedy algorithm for real time ride matching
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
    8.      M.add( (q,u) )
    9. return M, R
    '''
    def __init__(self, constraints_param):
        self.constraints_param = constraints_param

    def match(self, requests, drivers):
        '''
        drivers format:
        [{
            "userId": string,
            "location":  {
                "latitude": number,
                "longitude": number
            },
            "ongoingRide": [ requests ],
            "maxSeat": number
        }]

        requests format:
        [{
            "userId": string,
            "startLocation": {
                "latitude": number,
                "longitude": number
            },
            "endLocation": {
                "latitude": number,
                "longitude": number
            }
            "timestamp": number
        }]
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
            drivers_candidate = [ driver for driver in drivers if self.isSatisfyConstraints(request, driver) ]
            
            if len(drivers_candidate)==0:
                remainingRequests.append(request)
                continue
            
            # find driver index with min dist
            minDist = dist[0]
            minDistDriverIdx = 0
            for i in range(1, len(dist)):
                if(dist[i][0] < minDist[0]):
                    minDist = dist[i]
                    minDistDriverIdx = i
            
            mappings.append( (request, drivers_candidate[minDistDriverIdx]['userId']) )
            drivers_candidate[minDistDriverIdx]['ongoingRide'].append(request)
        
        return (mappings, remainingRequests)
            

    def isSatisfyConstraints(self, request, driver):
        '''
        1. driver.emptySeat > 0
        2. dist(driver.currentLocation, request.startLocation) < 1km
        3. if there is already passenger(s) in car ->  distance of best shared route < sum of 
        '''
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

    gMatcher = GreedyMatcher(None)
    M, R = gMatcher.match(requests, drivers)
    print('Q=[hku] D=[cu,polyu] test result: ')
    print('mapping: ')
    for q, d in M:
        print("  %s -> %s" %(q['userId'], d))
    print('remaining requests: ', R)

if __name__ == "__main__":
    greedyMatcherTest()