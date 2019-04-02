const express = require('express');
const router = express.Router();

const redisClient = require('../../../db/redisClient');
const { REDIS_KEYS } = require('../../../helpers/constants');
const { isDriverOnline } = require('../../../helpers/driver');
const { haversineDistance } = require('../../../helpers/distance');
const { RideLogs } = require('../../../models');


/* 
/api/driver/update
expected req.body format:
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
*/

const storeLocationToCache = (req, res, next) => {
    const userId = req.userIdentity._id.toString();

    redisClient.hset(
        REDIS_KEYS.DRIVER_LOCATION, 
        userId, 
        JSON.stringify(req.body),
        () => {
            next();
        }
    );
};

const detectAndHandleStartAndEndRide = (req, res, next) => {
    const userId = req.userIdentity._id.toString();

    redisClient.hget(
        REDIS_KEYS.DRIVER_ON_GOING_RIDE,
        userId,
        (err, data) => {
            

            let rideDetails = [];
            let newRideDetails = [];

            if(data!==undefined && data!==null){
                rideDetails = JSON.parse(data);
            }
            console.log(rideDetails);
            if(rideDetails.length === 0){
                // no ongoing ride, return all ride requests
                redisClient.lrange(REDIS_KEYS.RIDE_REQUEST, 0, -1, (error, requests)=>{
                    const parsedRequests = requests.map( (q)=> JSON.parse(q));
                    res.newRideDetails = parsedRequests;
                    
                    next();
                });
                
            }else{

                // filter out ride that already ended and change isOnCar flag of started ride
                rideDetails.forEach( (rideDetail) => {
                    const currentLocation = req.body.location;
                    const startDistance = haversineDistance(currentLocation, rideDetail.startLocation);
                    const endDistance = haversineDistance(currentLocation, rideDetail.endLocation);
                    const delta = 0.5;
                    if(startDistance <= delta && rideDetail.isOnCar===false){
                        // rider on car
                        rideDetail.isOnCar = true;
                        newRideDetails.push(rideDetail);
                    }else if(endDistance <= delta && rideDetail.isOnCar){
                        // ended ride, do not add to
                        RideLogs.findOneAndUpdate(
                            { $or: [ { 'id': rideDetail.id} ]  }, 
                            { 'finishedDate': new Date() }, 
                            {},
                            (error)=>{
                                if(error){
                                    console.log(error);
                                }else{
                                    console.log('updated ridelogs');
                                }
                            }
                        );
                        return;
                    }else{
                        // nothing happened
                        newRideDetails.push(rideDetail);
                    }
                });

                res.newRideDetails = newRideDetails;

                redisClient.hset(
                    REDIS_KEYS.DRIVER_ON_GOING_RIDE, 
                    userId, 
                    JSON.stringify(newRideDetails),
                    () => {
                        next();
                    }
                );
                
            }
        }
    );
};

const responseOnGoingRideDetails = (req, res) => {
    return res.status(200).json(res.newRideDetails);
};

const getAllDriversLocations = (req, res) => {
    
    const userId = req.userIdentity._id.toString();
    let isUserMatchedToADriver = false;
    let driverId = null;

    redisClient.hgetall(
        REDIS_KEYS.DRIVER_ON_GOING_RIDE,
        (err, allDriversRideDetails) => {

            // check if current user has matched ride
            if(allDriversRideDetails !== null){
                for(const key in allDriversRideDetails){
                    const rideDetails = JSON.parse(allDriversRideDetails[key]);
                    rideDetails.forEach( (ride)=>{
                        if(ride.userId === userId){
                            driverId = key;
                            isUserMatchedToADriver = true;
                        }
                    });
                }
            }

            if(isUserMatchedToADriver){
                // only return the matched driver location
                redisClient.hget(
                    REDIS_KEYS.DRIVER_LOCATION,
                    driverId,
                    (err, location) => {
                        let locationList = [];
                        if(location!==null){
                            locationList = [JSON.parse(location)].filter( x => isDriverOnline(x));
                        }
                        return res.status(200).json(locationList);
                    }
                );
            }else{
                // return all driver location
                redisClient.hgetall(
                    REDIS_KEYS.DRIVER_LOCATION,
                    (err, locations) => {
                        let locationList = [];

                        if(locations!==null){
                            locationList = Object.keys(locations)
                                .map( (key) => JSON.parse(locations[key]))
                                .filter( x => isDriverOnline(x));
                        }

                        return res.status(200).json(locationList);
                    }
                );
            }
            
        }
    );
    
};

router.post('/update',
    storeLocationToCache,
    detectAndHandleStartAndEndRide,
    responseOnGoingRideDetails
);

router.post('/get-all-drivers-location',
    getAllDriversLocations
);

module.exports = router;