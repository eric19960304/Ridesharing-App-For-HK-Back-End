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
from utils import gridWorldDistance, gridWorldDistanceMatrix

class Rebalancing:
    def __init__(self, constraints_param, useGridWorld=False):
        '''
        constraints_param format:
        {
                
        }
        '''
        self.assignList = [] 
        self.useGridWorld = useGridWorld             

    def _getDistanceMatrix(self, origins, destinations):
        if self.useGridWorld:
            return gridWorldDistanceMatrix(origins, destinations)
        else:
            return getDistanceMatrix(origins, destinations)

    def _getDistance(self, origin, destination):
        if self.useGridWorld:
            return gridWorldDistance(origin, destination)
        else:
            return getDistance(origin, destination)  

    def rebalance(self, requests, drivers, assignedR, assignedV):
        Vidle = [item for item in requests if item not in assignedR]
        Rko = [item for item in drivers if item not in assignedV]
        oneTripList = []
        for request in Vidle:
            for driver in Rko:
                distance = self._getDistance(driver["location"], request["startLocation"])
                oneTripList.append( (request, driver, distance) )
        oneTripList.sort(key=lambda tup: tup[2])
        minVidleRko = min(len(Vidle), len(Rko))
        i = 0
        for trip in oneTripList:
            if i == minVidleRko:
                break
            if (trip[0] in assignedR) == False and (trip[1] in assignedV) == False: 
                assignedR.append(trip[0])
                assignedV.append(trip[1])
                self.assignList.append(trip)
                i += 1