from time import time
from uuid import uuid4
import requests
import pymongo
from loc import loc
import sys

API_URL = 'http://localhost/'

class TestUser():
    def __init__(self, testUserId):
        self.testUserId = testUserId

        response = requests.post(url = API_URL+'auth/login', json={
            "email": 't'+str(testUserId),
            "password": "t"
        })
        self.headers = { 'JWT': response.json()['jwt'] }


    def sendRideRequest(self, startLocation, endLocation):
        body = {
            "startLocation":  {
                "latitude": startLocation['latitude'],
                "longitude" : startLocation['longitude']
            },
            "endLocation":  {
                "latitude": endLocation['latitude'], 
                "longitude" : endLocation['longitude']
            },
            "timestamp": round(time())
        }
        response = requests.post(url = API_URL+'api/rider/real-time-ride-request', json=body, headers=self.headers)
        print(response.json())

    def updateDriverLocation(self, location):
        body = {  
            "location": location,
            "timestamp": 1665418592527.194
        }
        response = requests.post(url = API_URL+'api/driver/update', json=body, headers=self.headers)
        print(response.json())

def createTestUsersIfNotExists():
    '''
    Create test user 1 - 100
    Assume that the jwt_secret of backend server is 'threeriders'
    '''
    mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
    threeridersDB = mongoclient["threeriders"]
    userDocuments = threeridersDB["users"]

    users = []
    for i in range(1, 101):
        user = {
            "pushTokens" : [],
            "activated" : True,
            "email" : "t"+str(i),
            "password" : "$2b$10$0NNUTnBOsvAmel.Rlmz.hucLGw5FjOJ6iMLoUhrJ.NlVPaOBobLB2",
            "nickname" : "Test user "+str(i),
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
    createTestUsersIfNotExists()

    if sys.argv[0]=='1':

        tusers = []
        for i in range(4):
            tusers.append( TestUser(i) )
        tusers[0].updateDriverLocation(loc['kowloon_tong_station'])
        tusers[1].updateDriverLocation(loc['mk_station'])
        tusers[2].sendRideRequest(loc['cityu'], loc['mk_station'])
    
    



