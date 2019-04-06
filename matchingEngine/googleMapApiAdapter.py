import googlemaps
import os
import ujson
from loc import loc

gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAP_API_KEY'])

def getDistance(origin, destination, getDuration=False):
    '''
    Format of origin and destination:
    { "latitude": int, "longitude": int }

    Return the distance/duration pair from a origin to a destination
    return (distance in m : int, duration in seconds : int)
    '''
    response = gmaps.distance_matrix(mode='driving', origins=origin, destinations=destination)

    duration_or_distance = 'distance'
    if(getDuration):
        duration_or_distance = 'duration'

    return response['rows'][0]['elements'][0][duration_or_distance]['value']

def getDistanceMatrix(origins, destinations, getDuration=False):
    '''
    Format of origins and destinations:
    [ { "latitude": int, "longitude": int } ]

    Return the distance matrix as 2D list
    return [ [ (distance in m : int, duration in seconds : int) ] ]
    # e.g. origins = [A, B], destinations = [C, D, E]
    # return:
    # [ [ A->C, A->D, A->E ],
    #   [ B->C, B->D, B->E ] ] where A->C means the distance/duration tuple from point A to point C
    '''
    matrixSize = len(origins)*len(destinations)
    if(matrixSize>81):
        raise Exception('matrix size='+ str(matrixSize) +' exceeds the limit (we don\' have enough credit in Google Cloud!')

    response = gmaps.distance_matrix(mode='driving', origins=origins, destinations=destinations)
    
    rowList = [ row['elements'] for row in response['rows'] ]

    duration_or_distance = 'distance'
    if(getDuration):
        duration_or_distance = 'duration'

    matrix = [ 
        [ element[duration_or_distance]['value'] for element in elements ] 
        for elements in rowList
    ]
    return matrix

def getDistanceTest():
    print(getDistance(loc['hku'], loc['hku']))

def getDistanceMatrixTest():
    origins = [loc['hku'], loc['cu'], loc['ust']]
    # destinations = [ loc['ust'], loc['polyu'], loc['cityu'] ]
    destinations = origins
    matrix = getDistanceMatrix(origins, destinations)
    print(matrix)

if __name__ == "__main__":
    print('Test all methods:')
    # getDistanceTest()
    getDistanceMatrixTest()
    print('Tests passed.')