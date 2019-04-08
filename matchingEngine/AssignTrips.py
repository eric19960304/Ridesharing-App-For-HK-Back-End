'''
RVGraph
(1) which requests can be pairwise combined: if share > single route then don't pairwise else pair wise
(2) which vehicles can serve which requests individually, given their current passengers
'''
from time import sleep, gmtime, strftime, time
import requests
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

class AssignTrips:
    def __init__(self,delayMax=5000):
        self.assignList = []    
        self.delayMax=delayMax 
          

    def Assignment(self,rtvGraph):
        oneRequestTrip = []
        twoRequestTrip = []
        assignList = []
        assignedV = []
        assignedR = []
        for trip in rtvGraph:
            if len(trip)==3 and len(trip[0]["ongoingRide"])==0:
                oneRequestTrip.append(trip)
            else:
                twoRequestTrip.append(trip)
        oneRequestTrip.sort(key=lambda tup: tup[2])
        twoRequestTrip.sort(key=lambda tup: tup[3])
        
        for trip in twoRequestTrip:
            if trip[3]<self.delayMax and trip[0] in assignedV == False and trip[1] in assignedR == False and trip[2] in assignedR == False: 
                assignedV.append(trip[0])
                assignedR.append(trip[1])
                assignedR.append(trip[2])
                assignList.append(trip)
        
        for trip in oneRequestTrip:
            if trip[2]<self.delayMax and trip[0] in assignedV == False and trip[1] in assignedR == False:
                assignedV.append(trip[0])
                assignedR.append(trip[1])
                assignList.append(trip)
            

            
        
                                


    '''
    return data structure example
    {
    'driver1',('request1'),('request2'),delayMin,
    'driver1',('request2'),('request3'),delayMin
              
    }
    '''

    

    
