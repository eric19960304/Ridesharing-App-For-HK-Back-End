'''
RVGraph
(1) which requests can be pairwise combined: if share > single route then don't pairwise else pair wise
(2) which vehicles can serve which requests individually, given their current passengers
'''
import redis
from time import sleep, gmtime, strftime, time
import ujson
import requests
import tsp
from googleMapApiAdapter import getDistance, getDistanceMatrix

# redis key name, refer to README for the data struture
RIDE_REQUEST = 'realTimeRideRequest'
DRIVER_LOCATION = 'driverLocation'
DRIVER_ON_GOING_RIDE = 'driverOngoingRide'

'''
{
    ('request1', 'request2'): distance,
    ('request1', 'request3'): distance,
}
'''

class RTVGraph:
    def __init__(self):
        self.rtvGraph = {}
        self.requestsGraph = {}                       

    def RTVGraphFindFeasibleTrips(self,requestsGraph,driverList):
        
        for (riderLocationJson, riderLocationJson2) in requestsGraph:
            for driverJson in driverList:
                if len(driverJson["ongoingRide"]) == 0:
                locationList = []
                locationList.append( driverLocationJson )
                locationList.append( riderLocationJson[startLocation])
                locationList.append( riderLocationJson2[startLocation] )
                distanceMatrix = getDistanceMatrix(locationList, locationList)

                delaylist = []
                delaylist.append((distanceMatrix[0][1] + distanceMatrix[1][2]-distanceMatrix[0][2])+(distanceMatrix[1][2]+distanceMatrix[2][3]-distanceMatrix[1][3]))
                delaylist.append(distanceMatrix[0][1] + distanceMatrix[1][3]+ distanceMatrix[3][2]- distanceMatrix[0][2])
                delaylist.append(distanceMatrix[1][0] + distanceMatrix[0][2]+distanceMatrix[2][3]- distanceMatrix[1][3])
                delaylist.append((distanceMatrix[1][0] + distanceMatrix[0][3]-distanceMatrix[1][3])+(distanceMatrix[0][3] + distanceMatrix[3][2]-distanceMatrix[0][2]))
                
                delayMin=min(delaylist)
                index=delaylist.index(min(delaylist))

                if delayMin<10000:  
                    if index<2:
                        if distanceMatrix[0][1] + distanceMatrix[1][2]<5000:
                             self.rtvGraph.append(driverJson,request,delayMin,index)
                    else:
                        if distanceMatrix[0][2] + distanceMatrix[2][1]<5000:
                            self.rtvGraph.append(driverJson,request,delayMin,index)
                   
                   
    
    self.rtvGraph.append(rvGraph)

            
                
                                


    '''
    return data structure example
    {
               (userID, delayDistance)
    'driver1':[('request1', 140),('request2', 118),('request3', 75)],
    'driver2':[('request1', 172),('request2', 220)],
    }
    '''

    '''TSP Link:https://pypi.org/project/tsp/'''

    
