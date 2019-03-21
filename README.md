# HKUCS FYP Back End Server for Ridesharing App


Also see the App repository: https://github.com/eric19960304/Ridesharing-App-For-HK

prerequisite:

1. nodejs version 10.x.x installed

2. clean mongodb running on localhost:27017 ( [Windows](https://stackoverflow.com/questions/20796714/how-do-i-start-mongo-db-from-windows) | [Mac](https://stackoverflow.com/questions/18452023/installing-and-running-mongodb-on-osx) )

3. yarn with version >=1.12.3 installed

4. redis running on port 6379 (default port)


Required enviroment variables in server (see config.js):
* MONGODB_PASSWORD
* PROD
* JWT_SECRET
* GMAIL_PASSWORD (for hkucsfyp2018threeriders@gmail.com, you can change the email address in config.js)
* GOOGLE_MAP_API_KEY



To install all the packages (under project's root directory):

`yarn`

To run the server in development mode:

`yarn start`

To run the server in production mode (all env variables should be set):

`yarn run prod`



# Matching Engine

prerequisite:

1. Python >=3.6

2. pip3 (which is for python 3) command avaliable in your terminal

3. clean mongodb running on localhost:27017 ( [Windows](https://stackoverflow.com/questions/20796714/how-do-i-start-mongo-db-from-windows) | [Mac](https://stackoverflow.com/questions/18452023/installing-and-running-mongodb-on-osx) )

4. redis running on port 6379 (default port)



To install all the packages (under /matchingEngine directory):

`pip3 install -r requirements.txt`

To run the server "engine_v1":

`python3 engine_v1.py`




List of used Redis keys

1. realTimeRideRequest

A redis list that act as a match queue, where each element in list is a JSON string representing a ride request from passengers.

Structure of a ride request JSON:
```
{
    userId: string,
    startLocation: {
        latitude: number,
        longitude: number
    },
    endLocation: {
        latitude: number,
        longitude: number
    }
    timestamp: number
}
```

2. driverLocation

A redis hash with driver's userId as key, a JSON string representing his/her location as value.

Structure of the location JSON:
```
{
    "location":  {
        "accuracy": number,
        "altitude": number,
        "altitudeAccuracy": number,
        "heading": number,
        "latitude": number,
        "longitude": number,
        "speed": number
    },
    "timestamp": number
}
```

3. driverMatchedDetail

A redis hash with driver's userId as key, a JSON string representing a list of his/her matched ride(s) details as value

Structure of the ride details JSON:
```
[
    {
        userId: string,   // matched rider id
        startLocation: {
            latitude: number,
            longitude: number
        },
        endLocation: {
            latitude: number,
            longitude: number
        }
        timestamp: number
    },
    ...
]
```