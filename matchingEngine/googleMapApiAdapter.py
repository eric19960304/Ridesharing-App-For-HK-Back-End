import googlemaps
import os
import ujson
import univLoc

gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAP_API_KEY'])

def getDistance(origin, destination):
    '''
    Format of origin and destination:
    { "latitude": int, "longitude": int }

    Return the distance/duration pair from a origin to a destination
    return (distance in km : int, duration in seconds : int)
    '''
    response = gmaps.distance_matrix(mode='driving', origins=origin, destinations=destination)
    
    return (response['rows'][0]['elements'][0]['distance']['value'],
            response['rows'][0]['elements'][0]['duration']['value'] ) 

def getDistanceMatrix(origins, destinations):
    '''
    Format of origins and destinations:
    [ { "latitude": int, "longitude": int } ]

    Return the distance matrix as 2D list
    return [ [ (distance in km : int, duration in seconds : int) ] ]
    # e.g. origins = [A, B], destinations = [C, D, E]
    # return:
    # [ [ A->C, A->D, A->E ],
    #   [ B->C, B->D, B->E ] ] where A->C means the distance/duration tuple from point A to point C
    '''
    response = gmaps.distance_matrix(mode='driving', origins=origins, destinations=destinations)
    
    rowList = [ row['elements'] for row in response['rows'] ]
    matrix = [ 
        [ (element['distance']['value'], element['duration']['value'] ) for element in elements ] 
        for elements in rowList
    ]
    return matrix

def getDistanceTest():
    print(getDistance(univLoc.hku, univLoc.cu))

def getDistanceMatrixTest():
    origins = [univLoc.hku, univLoc.cu]
    destinations = [ univLoc.ust, univLoc.polyu, univLoc.cityu ]
    matrix = getDistanceMatrix(origins, destinations)
    print(matrix)

if __name__ == "__main__":
    print('Test all methods:')
    getDistanceTest()
    getDistanceMatrixTest()
    print('Tests passed.')