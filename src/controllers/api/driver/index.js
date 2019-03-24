const express = require('express');
const router = express.Router();

const redisClient = require('../../../db/redisClient');
const { REDIS_KEYS } = require('../../../helpers/constants');
const { isDriverOnline } = require('../../../helpers/driver');
const { haversineDistance } = require('../../../helpers/distance');


/* 
/api/driver/location-update
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

const detectAndHandleEndOfRide = (req, res, next) => {
    const userId = req.userIdentity._id.toString();

    redisClient.hget(
        REDIS_KEYS.DRIVER_ON_GOING_RIDE,
        userId,
        (err, rideDetails) => {
            if(rideDetails===null){
                next();
            }else{
                const originRideDetails = JSON.parse(rideDetails);
                let newRideDetails = JSON.parse(rideDetails);
                newRideDetails = newRideDetails.filter( (rideDetail) => {
                    const endLocation = rideDetail.endLocation;
                    const currentLocation = req.body.location;
                    const distance = haversineDistance(currentLocation, endLocation);
                    return Boolean(distance > 0.5);
                });

                if(newRideDetails.length===0){
                    redisClient.hdel(
                        REDIS_KEYS.DRIVER_ON_GOING_RIDE, 
                        userId,
                        () => {
                            next();
                        }
                    );
                }else{
                    if(newRideDetails.length !== originRideDetails.length){
                        redisClient.hset(
                            REDIS_KEYS.DRIVER_ON_GOING_RIDE, 
                            userId, 
                            JSON.stringify(newRideDetails),
                            () => {
                                next();
                            }
                        );
                    }else{
                        next();
                    }
                }
            }
        }
    );
};

const storeLocationToCache = (req, res) => {
    const latitude = req.body.location.latitude;
    const longitude = req.body.location.longitude;
    const userId = req.userIdentity._id.toString();

    redisClient.hset(
        REDIS_KEYS.DRIVER_LOCATION, 
        userId, 
        JSON.stringify(req.body),
        () => {
            return res.status(200).json({
                result: `user location updated: userId=${userId}, lat=${longitude}, long=${latitude}`
            });
        }
    );
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

router.post('/location-update',
    detectAndHandleEndOfRide,
    storeLocationToCache
);

router.post('/get-all-drivers-location',
    getAllDriversLocations
);

module.exports = router;