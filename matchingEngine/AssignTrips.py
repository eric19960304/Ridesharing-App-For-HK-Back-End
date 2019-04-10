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
          

    def assignment(self,rtvGraph, showDetails=False):
        oneRequestTrip = []
        twoRequestTrip = []

        for trip in rtvGraph:
            if len(trip)==3 and len(trip[0]["ongoingRide"])==0:
                oneRequestTrip.append(trip)
            else:
                twoRequestTrip.append(trip)
        
        oneRequestTrip.sort(key=lambda tup: tup[-1])
        twoRequestTrip.sort(key=lambda tup: tup[-1])
        if showDetails:
            print("oneRequestTrip: ",oneRequestTrip)
            print("twoRequestTrip: ",twoRequestTrip)
        for trip in twoRequestTrip:
            # print("trip[3]: ",trip[3])
            # print("self.delayMax: ",self.delayMax)
            # print("trip[0] ",trip[0])
            # print("trip[1] ",trip[1])
            # print("trip[2] ",trip[2])
            # print(trip[0] in self.assignedV)
            # print(trip[1] in self.assignedR)
            # print(trip[2] in self.assignedR)
            print(trip[-1] in self.assignedR)
            if trip[-1]<self.delayMax and (trip[0] not in self.assignedV) and (trip[1] not in self.assignedR): 
               #print("hi ",trip[2])
                if len(trip)==4:
                    if (trip[2] not in self.assignedR):
                        self.assignList.append((trip[1],trip[0]))
                        self.assignList.append((trip[2],trip[0]))
                        self.assignedV.append(trip[0])
                        self.assignedR.append(trip[1])
                        self.assignedR.append(trip[2])
                else:
                    print ('loop',' trip1:',trip[1],' trip0:',trip[0] )
                    self.assignList.append((trip[1],trip[0]))
                    self.assignedR.append(trip[1])
                    self.assignedV.append(trip[0])
               

        
        for trip in oneRequestTrip:
            if showDetails:
                print("trip[0] ",trip[0] not in self.assignedV)
                print("trip[1] ",trip[1] not in self.assignedR)
                print("trip[2] ",trip[2])
            if trip[2]<self.delayMax and (trip[0] not in self.assignedV) and (trip[1] not in self.assignedR):
                self.assignedV.append(trip[0])
                self.assignedR.append(trip[1])
                self.assignList.append((trip[1],trip[0]))
            ''' (driver,request,request2,delayMin)    
                (driver,request,delayMin)  '''

            
        
                                


    '''
    return data structure example
    {
    'driver1',('request1'),('request2'),delayMin,
    'driver1',('request2'),('request3'),delayMin
              
    }
    '''

    

    
