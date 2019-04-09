'''
Rebalancing
min(Vidle.length, Rko.length)
for i in min(Vidle, Rko):
    eachDistance = distanceOfEach(Vidle, Rko)
sort(eachDistance)
match(eachDistance)

(1) assign request if there are so much assigned requests and idle vehical
(2) assign request if that request wait for long time 

or
paper: assign min(Vidle, Rko) no matter how far away
'''
from googleMapApiAdapter import getDistance, getDistanceMatrix

class Rebalancing:
    def __init__(self, constraints_param, useGridWorld=False):
        '''
        constraints_param format:
        {
                
        }
        '''
        self.assignList = [] 
        self.useGridWorld = useGridWorld             

    def rebalance(self, requests, drivers, assignedR, assignedV):
        Vidle = [item for item in requests if item not in assignedR]
        Rko = [item for item in drivers if item not in assignedV]
        rvList = []
        for request in Vidle:
            for driver in Rko:
                distance = getDistance(driver["location"], request["startLocation"])
                rvList.append( (request, driver, distance) )
        rvList.sort(key=lambda tup: tup[2])
        minVidleRko = min(len(Vidle), len(Rko))
        self.assignList = rvList[0..(minVidleRko-1)]