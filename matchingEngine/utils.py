from math import radians, cos, sin, asin, sqrt
from loc import loc

def haversineDistance(location1, location2):
    """
    Calculate the great circle distance between two points in meters
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1 = location1['latitude']
    lon1 = location1['longitude']
    lat2 = location2['latitude']
    lon2 = location2['longitude']
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000

def gridWorldDistance(location1, location2):
    '''
    location: ( int, int)
    '''
    return abs(location1[0]-location2[0]) + abs(location1[1]-location2[1])

def gridWorldDistanceMatrix(origins, destinations):
    matrix = []
    for o in origins:
        row = []
        for d in destinations:
            row.append( gridWorldDistance(o, d) )
        matrix.append( row )
    return matrix

if __name__ == "__main__":
    print('test')
    # print(haversineDistance(loc['hku'], loc['cu']))
    distMatrix = gridWorldDistanceMatrix( [(3,5), (10, 11), (6, 6), (8, 5)], [(91, 5), (50, 50), (31, 42)] )
    print( len(distMatrix), len(distMatrix[0]) )
    print(distMatrix)