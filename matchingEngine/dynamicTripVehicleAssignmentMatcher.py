import googleMapApiAdapter as gMapApi
from loc import loc
from RVGraph import RVGraph

class DynamicTripVehicleAssignmentMatcher():
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
        self.maxMatchDistance = constraints_param['maxMatchDistance']
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
        g = RVGraph()
        g.RVGraphPairwiseRequests(requests)
        print(g.requestsGraph)
        g.RVGraphPairwiseDriverRequest(requests, drivers)
        print(g.rvGraph)
        return ([], requests)

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
        }
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
            "ongoingRide": [onGoingReq1],
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