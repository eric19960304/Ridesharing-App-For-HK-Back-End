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

const getAllRequests = (req, res, next) => {

    redisClient.lrange(REDIS_KEYS.RIDE_REQUEST, 0, -1, (error, requests)=>{
        const parsedRequests = requests.map( (q)=> JSON.parse(q));
        res.allRideRequests = parsedRequests;
        
        next();
    });
};

const detectAndHandleStartAndEndRide = (req, res, next) => {
    const userId = req.userIdentity._id.toString();

    redisClient.hget(
        REDIS_KEYS.DRIVER_ON_GOING_RIDE,
        userId,
        (err, data) => {
            

            let prevOnGoingRideDetails = [];
            let onGoingRideDetails = [];

            if(data!==undefined && data!==null){
                prevOnGoingRideDetails = JSON.parse(data);
            }

            
            if(prevOnGoingRideDetails.length === 0){
                res.onGoingRideDetails = [];
                next();

            }else{

                // filter out ride that already ended and change isOnCar flag of started ride
                prevOnGoingRideDetails.forEach( (rideDetail) => {
                    const currentLocation = req.body.location;
                    const startDistance = haversineDistance(currentLocation, rideDetail.startLocation);
                    const endDistance = haversineDistance(currentLocation, rideDetail.endLocation);
                    const delta = 0.5;
                    if(startDistance <= delta && rideDetail.isOnCar===false){
                        // rider on car
                        rideDetail.isOnCar = true;
                        onGoingRideDetails.push(rideDetail);
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
                        onGoingRideDetails.push(rideDetail);
                    }
                });

                res.onGoingRideDetails = onGoingRideDetails;

                redisClient.hset(
                    REDIS_KEYS.DRIVER_ON_GOING_RIDE, 
                    userId, 
                    JSON.stringify(onGoingRideDetails),
                    () => {
                        next();
                    }
                );
                
            }
        }
    );
};

const responseOnGoingRideDetails = (req, res) => {
    return res.status(200).json({
        allRideRequests: res.allRideRequests,
        onGoingRides: res.onGoingRideDetails
    });
};

const checkIfSearhcing = (req, res, next) => {
    const userId = req.userIdentity._id.toString();
    redisClient.lrange(
        REDIS_KEYS.RIDE_REQUEST,
        0,
        -1,
        (err, rideReqs) => {
            let found = false;
            rideReqs.forEach( r =>{
                const rideReq = JSON.parse(r);
                if(rideReq.userId==userId){
                    found=true;
                }
            });
            req.isSearching = found;
            next();
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
                        let matchedLocation = [];
                        if(location!==null){
                            matchedLocation = JSON.parse(location);
                        }

                        redisClient.hgetall(
                            REDIS_KEYS.DRIVER_LOCATION,
                            (err, locations) => {
                                let allLocationList = [];
        
                                if(locations!==null){
                                    allLocationList = Object.keys(locations)
                                        .map( (key) => JSON.parse(locations[key]))
                                        .filter( x => isDriverOnline(x));
                                }
        
                                return res.status(200).json({
                                    matchedDriver: matchedLocation,
                                    allDrivers: allLocationList,
                                    isSearching: req.isSearching
                                });
                            }
                        );
                    }
                );
            }else{
                // return all driver location
                redisClient.hgetall(
                    REDIS_KEYS.DRIVER_LOCATION,
                    (err, locations) => {
                        let allLocationList = [];

                        if(locations!==null){
                            allLocationList = Object.keys(locations)
                                .map( (key) => JSON.parse(locations[key]))
                                .filter( x => isDriverOnline(x));
                        }

                        return res.status(200).json({
                            matchedDriver: null,
                            allDrivers: allLocationList,
                            isSearching: req.isSearching
                        });
                    }
                );
            }
            
        }
    );
    
};

router.post('/update',
    storeLocationToCache,
    getAllRequests,
    detectAndHandleStartAndEndRide,
    responseOnGoingRideDetails
);

router.post('/get-all-drivers-location',
    checkIfSearhcing,
    getAllDriversLocations
);

module.exports = router;