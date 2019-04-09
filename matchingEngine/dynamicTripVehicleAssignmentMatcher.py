import googleMapApiAdapter as gMapApi
from loc import loc
from RVGraph import RVGraph
from RTVGraph import RTVGraph
from AssignTrips import AssignTrips

class DynamicTripVehicleAssignmentMatcher:
    def __init__(self, constraints_param, useGridWorld=False):
        '''
        constraints_param:
        {
            # max distance between driver's location and request's start point allowed to be matched
            "maxMatchDistance": number
        }
        useGridWorld:
            True or False, indicate whether use grid world to do testing
        '''
        #self.maxMatchDistance = constraints_param['maxMatchDistance']
        self.constraints_param = constraints_param
        self.useGridWorld = useGridWorld

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
            "timestamp": number,
            "isOnCar": False,
        ]
        drivers format:
        [{  "userId": string,
            "location":  {
                "latitude": number,
                "longitude": number
            },
            "ongoingRide": [ {
                "id": string,
                "userId": string,
                "startLocation": {
                    "latitude": number,
                    "longitude": number
                },
                "endLocation": {
                    "latitude": number,
                    "longitude": number
                }
                "timestamp": number,
                "isOnCar": boolean,         <---- if passenger on the car
            } ],
            "capacity": number,
            "timestamp": number           }]
        '''
        
        #constraints_param = {"maxMatchDistance": 5000}
        g = RVGraph(self.constraints_param)
        g.RVGraphPairwiseRequests(requests)
        print("rrGraph: ", g.requestsGraph)
        g.RVGraphPairwiseDriverRequest(requests, drivers)
        print("rvGraph: ",g.rvGraph)
        g2 = RTVGraph(self.constraints_param)
        g2.RTVGraphFindFeasibleTrips(g, drivers)
        print("rtvGraph: ",g2.rtvGraph)
        #rtvGraph=[({'userId': 'Antony', 'location': {'latitude': 22.4134546, 'longitude': 114.2105288}, 'ongoingRide': [], 'capacity': 4}, {'id': '2', 'userId': 'Tony', 'startLocation': {'latitude': 22.4134546, 'longitude': 114.2105288}, 'endLocation': {'latitude': 22.283551, 'longitude': 114.134292}, 'timestamp': 1553701760965, 'isOnCar': False}, {'id': '4', 'userId': 'Alex', 'startLocation': {'latitude': 22.4134546, 'longitude': 114.2105288}, 'endLocation': {'latitude': 22.2882899, 'longitude': 114.1416011}, 'timestamp': 1553701760965, 'isOnCar': False}, 23), ({'userId': 'Antony1', 'location': {'latitude': 22.4134546, 'longitude': 114.2105288}, 'ongoingRide': [], 'capacity': 4}, {'id': '2', 'userId': 'Tony', 'startLocation': {'latitude': 22.4134546, 'longitude': 114.2105288}, 'endLocation': {'latitude': 22.283551, 'longitude': 114.134292}, 'timestamp': 1553701760965, 'isOnCar': False}, {'id': '4', 'userId': 'Alex', 'startLocation': {'latitude': 22.4134546, 'longitude': 114.2105288}, 'endLocation': {'latitude': 22.2882899, 'longitude': 114.1416011}, 'timestamp': 1553701760965, 'isOnCar': False}, 23)]
        g3=AssignTrips(self.constraints_param["maxCost"])
        g3.Assignment(g2.rtvGraph)
        
        print("assignment: ",g3.assignList)
        print("assigned V: ",g3. assignedV)
        print("assigned R: ",g3. assignedR)
        unAssignedR=[]
        for r,d in g3.assignList:
            d["ongoingRide"].append(r)
        for r in requests:
            if r not in g3.assignedR:
                unAssignedR.append(r)
        return (g3.assignList, unAssignedR)

def Test():
    requests = [
        {
            "id": '1',
            "userId": 'Eric',
            "startLocation": loc['city_one'],
            "endLocation": loc['sai_ying_pun_station'],
            "timestamp": 1553701200965,
            "isOnCar": False
        },
        {
            "id": '2',
            "userId": 'Tony',
            "startLocation": loc['cu'],
            "endLocation": loc['hku'],
            "timestamp": 1553701760965,
            "isOnCar": False
        },
        {
            "id": '4',
            "userId": 'alex',
            "startLocation": loc['cu'],
            "endLocation": loc['sai_ying_pun_station'],
            "timestamp": 1553701760965,
            "isOnCar": False
        },
      
    ]

    onGoingReq1 = {
        "id": '3',
        "userId": 'David',
        "startLocation": loc['cu'],
        "endLocation": loc['hku'],
        "timestamp": 1553701060965,
        "isOnCar": False
    }


    drivers = [
        {
            "userId": 'Antony',
            "location":  loc['cu'],
            "ongoingRide": [],
            "capacity": 4
        },
        {
            "userId": 'Antony1',
            "location":  loc['cu'],
            "ongoingRide": [],
            "capacity": 4
        },
        {
            "userId": 'Elven',
            "location":  loc['polyu'],
            "ongoingRide": [],
            "capacity": 4
        }
    ]

    dMatcher = DynamicTripVehicleAssignmentMatcher({ 'maxMatchDistance': 1 })
    M, R = dMatcher.match(requests, drivers)

if __name__ == "__main__":
    Test()