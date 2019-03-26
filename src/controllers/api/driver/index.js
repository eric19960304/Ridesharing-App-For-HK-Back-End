const express = require('express');
const router = express.Router();

const redisClient = require('../../../db/redisClient');
const { REDIS_KEYS } = require('../../../helpers/constants');
const { isDriverOnline } = require('../../../helpers/driver');
const { haversineDistance } = require('../../../helpers/distance');


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

const detectAndHandleEndOfRide = (req, res, next) => {
    const userId = req.userIdentity._id.toString();

    redisClient.hget(
        REDIS_KEYS.DRIVER_ON_GOING_RIDE,
        userId,
        (err, rideDetails) => {
            if(rideDetails===null){
                // no ongoing ride
                let newRideDetails = [];
                res.newRideDetails = newRideDetails;
                next();
            }else{
                // has at least one ongoing ride
                let newRideDetails = JSON.parse(rideDetails);
                newRideDetails = newRideDetails.filter( (rideDetail) => {
                    const endLocation = rideDetail.endLocation;
                    const currentLocation = req.body.location;
                    const distance = haversineDistance(currentLocation, endLocation);
                    return Boolean(distance > 0.5);
                });

                res.newRideDetails = newRideDetails;
                next();
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
    detectAndHandleEndOfRide,
    responseOnGoingRideDetails
);

router.post('/get-all-drivers-location',
    getAllDriversLocations
);

module.exports = router;