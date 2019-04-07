from time import time
from uuid import uuid4
import requests
import pymongo
from loc import loc
import sys
import redis
import ujson

API_URL = 'http://localhost/'

class TestUser:
    def __init__(self, email):
        self.email = email

        response = requests.post(url = API_URL+'auth/login', json={
            "email": email,
            "password": "t"
        })
        self.headers = { 'JWT': response.json()['jwt'] }


    def sendRideRequest(self, startLocation, endLocation):
        body = {
            "nickname": self.email,
            "startLocation":  {
                "latitude": startLocation['latitude'],
                "longitude" : startLocation['longitude']
            },
            "endLocation":  {
                "latitude": endLocation['latitude'], 
                "longitude" : endLocation['longitude']
            },
            "timestamp": round(time()),
            "isOnCar": False
        }
        response = requests.post(url = API_URL+'api/rider/real-time-ride-request', json=body, headers=self.headers)
        print(response.json())

    def updateDriverLocation(self, location):
        body = {
            "nickname": self.email,
            "location": location,
            "timestamp": 1665418592527.194
        }
        response = requests.post(url = API_URL+'api/driver/update', json=body, headers=self.headers)
        print(response.json())

def createTestUsersIfNotExists():
    '''
    Assume that the jwt_secret of backend server is 'threeriders'
    '''
    mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
    threeridersDB = mongoclient["threeriders"]
    userDocuments = threeridersDB["users"]

    users = []
    userEmailsAndNickNames = ['D1', 'D2', 'R1', 'R2', 'R3', 'R4']
    for email in userEmailsAndNickNames:
        user = {
            "pushTokens" : [],
            "activated" : True,
            "email" : email,
            "password" : "$2b$10$0NNUTnBOsvAmel.Rlmz.hucLGw5FjOJ6iMLoUhrJ.NlVPaOBobLB2",
            "nickname" : email,
            "isDriver" : True,
            "carplate" : "12345",
            "contact" : "52252872"
        }

        userDoc = userDocuments.find_one({
            'email': user['email']
        })
        if(userDoc==None):
            users.append(user)
    if(len(users)>0):
        print("Creating %d Test users..."%(len(users)))
        userDocuments.insert_many(users)
    else:
        print('Test Users already exists')

if __name__ == "__main__":
    if len(sys.argv) < 2 or (sys.argv[1]!='1' and sys.argv[1]!='2'):
        print('Usage: python caseStudy.py [1 or 2]')
        exit()

    createTestUsersIfNotExists()

    if sys.argv[1]=='1':

        d1 = TestUser('D1')
        d2 = TestUser('D2')
        r1 = TestUser('R1')
        r2 = TestUser('R2')
        d1.updateDriverLocation(loc['case1_D1'])
        d2.updateDriverLocation(loc['case1_D2'])
        r1.sendRideRequest(loc['case1_R1_start'], loc['case1_R1_end'])
        r2.sendRideRequest(loc['case1_R2_start'], loc['case1_R2_end'])
        print('Case 1: all requests sent')

    if sys.argv[1]=='2':

        # set request 2 to driver2's ongoing ride list on Redis
        mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
        threeridersDB = mongoclient["threeriders"]
        userDocuments = threeridersDB["users"]

        userDoc = userDocuments.find_one({
            'email': 'D2'
        })
        d2UserId = str(userDoc['_id'])

        r2 = {
            "nickname": "R2",
            "startLocation": loc['case2_R2_start'],
            "endLocation":  loc['case2_R2_end'],
            "timestamp": round(time()),
            "isOnCar": False
        }
        onGoingJson = ujson.dumps([r2])
        redisConn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        redisConn.hset('driverOngoingRide', d2UserId, onGoingJson)
        print('stored R2 on Redis')
        
        d1 = TestUser('D1')
        d2 = TestUser('D2')
        r1 = TestUser('R1')
        r3 = TestUser('R3')
        r4 = TestUser('R4')
        d1.updateDriverLocation(loc['case2_D1'])
        d2.updateDriverLocation(loc['case2_D2'])
        r1.sendRideRequest(loc['case2_R1_start'], loc['case2_R1_end'])
        r3.sendRideRequest(loc['case2_R3_start'], loc['case2_R3_end'])
        r4.sendRideRequest(loc['case2_R4_start'], loc['case2_R4_end'])
        print('Case2: all requests sent')