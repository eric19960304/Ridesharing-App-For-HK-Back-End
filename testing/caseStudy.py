from time import time
from uuid import uuid4

def makeRideRequest(startLat, startLong, endLat, endLong, rideId=None):
    if rideId==None:
        rideId = uuid4()
    return {
        "id": rideId,
        "startLocation":  {
            "latitude": startLat,
            "longitude" : startLong
        },
        "endLocation":  {
            "latitude": endLat, 
            "longitude" : endLong
        },
        "timestamp": round(time())
    }

def makeDriver(driverid):
    # TODO
    pass
