import googlemaps
import os
import ujson

# 'rows': contains lists of distances from an origin to each destinations
# 'elements': each elements is a distance from the ith origin to jth destinations
# e.g. origins = [A B], destinations = [C D E]
# results (also see distance_matrix_response_format.txt for the original google map api response format):
# [ [ A->C, A->D, A->E ],
#   [ B->C, B->D, B->E ] ]

gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAP_API_KEY'])

def getDistance(origin, destination):
    '''
    Return the distance/duration pair from a origin to a destination in km
    return (int, int)
    '''
    response = gmaps.distance_matrix(origins=origin, destinations=destination)
    
    return (response['rows'][0]['elements'][0]['distance']['value'],
            response['rows'][0]['elements'][0]['duration']['value'] ) 

def getDistanceMatrix(origins, destinations):
    '''
    Return the distance matrix as 2D list
    return [ [ (int, int) ] ]
    '''
    response = gmaps.distance_matrix(origins=origins, destinations=destinations)
    
    rowList = [ row['elements'] for row in response['rows'] ]
    matrix = [ 
        [ (element['distance']['value'], element['duration']['value'] ) for element in elements ] 
        for elements in rowList
    ]
    return matrix

def getDistanceTest():
    # HKU
    origin={
        "latitude": 22.283551,
        "longitude": 114.134292
    }

    # CU
    destination={
        "latitude": 22.416678,
        "longitude": 114.209649
    }

    print(getDistance(origin, destination))

def getDistanceMatrixTest():
    origins = [
        # HKU
        {
            "latitude": 22.283551,
            "longitude": 114.134292
        },
        # CU
        {
            "latitude": 22.416678,
            "longitude": 114.209649
        }
    ]

    destinations = [
        # UST
        {
            "latitude": 22.335998,
            "longitude": 114.263560
        },
        # PolyU
        {
            "latitude": 22.304239, 
            "longitude": 114.179677
        },
        # CityU
        {
            "latitude": 22.337488, 
            "longitude": 114.171442
        },
    ]

    matrix = getDistanceMatrix(origins, destinations)
    print(matrix)

if __name__ == "__main__":
    print('Test all methods:')
    getDistanceTest()
    getDistanceMatrixTest()
    print('Tests passed.')