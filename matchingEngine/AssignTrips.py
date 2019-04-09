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
        self.assignedV = []
        self.assignedR = []
        self.delayMax=delayMax 
          

    def Assignment(self,rtvGraph):
        oneRequestTrip = []
        twoRequestTrip = []

        for trip in rtvGraph:
            #print("len(trip): ",len(trip))
            #print("twoRequestTrip: ",twoRequestTrip)
            if len(trip)==3 and len(trip[0]["ongoingRide"])==0:
                oneRequestTrip.append(trip)
            else:
                twoRequestTrip.append(trip)
        
        oneRequestTrip.sort(key=lambda tup: tup[2])
        twoRequestTrip.sort(key=lambda tup: tup[3])
        #print("oneRequestTrip: ",oneRequestTrip)
        for trip in twoRequestTrip:
            # print("trip[3]: ",trip[3])
            # print("self.delayMax: ",self.delayMax)
            # print("trip[0] ",trip[0])
            # print("trip[1] ",trip[1])
            # print("trip[2] ",trip[2])
            # print(trip[0] in self.assignedV)
            # print(trip[1] in self.assignedR)
            # print(trip[2] in self.assignedR)
            if trip[3]<self.delayMax and (trip[0] in self.assignedV) == False and (trip[1] in self.assignedR) == False and (trip[2] in self.assignedR) == False: 
               #print("hi ",trip[2])
                self.assignedV.append(trip[0])
                self.assignedR.append(trip[1])
                self.assignedR.append(trip[2])
                self.assignList.append((trip[1],trip[0]))
                self.assignList.append((trip[2],trip[0]))
        
        for trip in oneRequestTrip:
            if trip[2]<self.delayMax and trip[0] in self.assignedV == False and trip[1] in self.assignedR == False:
                self.assignedV.append(trip[0])
                self.assignedR.append(trip[1])
                self.assignList.append((trip[1],trip[0]))
            

            
        
                                


    '''
    return data structure example
    {
    'driver1',('request1'),('request2'),delayMin,
    'driver1',('request2'),('request3'),delayMin
              
    }
    '''

    

    
