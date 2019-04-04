import os
import ujson
import loc
import requests
import utils

'''
Seems not work for Hong Kong
'''

API_URL = 'http://www.mapquestapi.com/directions/v2/routematrix?key=0qqFuoPaBANYKr3qRGRGk7RCWg4fNo6q'

def getDistanceMatrix(locations, getDuration=False):
    '''
    Format of origins and destinations:
    [ { "latitude": int, "longitude": int } ]

    Return the distance matrix as 2D list
    return [ [ (distance in m : int, duration in seconds : int) ] ]
    # e.g. locations = [A, B, C]
    # return:
    # [ [ 0, A->B, A->C ],
    #   [ B->A, 0, B->C ],
    #   [ C->A, C->B, 0 ]  ] where A->C means the distance/duration tuple from point A to point C
    '''
    matrixSize = len(locations)*len(locations)
    if(matrixSize>81):
        raise Exception('matrix size='+ str(matrixSize) +' exceeds the limit (we don\' have enough credit in Google Cloud!')

    latLongLocations = [ 
        { "latLng": {
                "lat": l['latitude'],
                "lng": l['longitude']
            }   
        }
        for l in locations
    ]

    jsonBody = {
        "locations": latLongLocations,
        "options": {
            "allToAll": True,
            "unit": "k"
        }
    }

    response = requests.post(url = API_URL, json=jsonBody )
    responseJson = response.json()
    
    if(getDuration):
        return responseJson['distance']
    else:
        return responseJson['time']

def getDistanceMatrixTest():
    locations = [ loc.hku, loc.cu, loc.ust ]
    matrix = getDistanceMatrix(locations)
    print(utils.haversineDistance(loc.hku, loc.cu))
    print(matrix)

if __name__ == "__main__":
    print('Test all methods:')
    getDistanceMatrixTest()
    print('Tests passed.')