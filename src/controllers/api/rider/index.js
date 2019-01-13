const express = require('express');

const redisClient = require('../../../db/redisClient');
const { REAL_TIME } = require('../../../helpers/constants');
const config = require('../../../../config');
const networkClient = require('../../../helpers/networkClient');

const router = express.Router();

/* 
/api/rider/real-time-ride-request
expected req.body format: {
        location: {
            latitude: number,
            longitude: number
        },
        destination: {
            latitude: number,
            longitude: number
        }
        timestamp: number
}
*/

const checkRiderStatus = (req, res, next) => {
    const userId = req.userIdentity._id;
    redisClient.hget(REAL_TIME.REDIS_KEYS.RIDE_STATUS, userId, (err, status)=>{
        if(err){
            console.log("something wrong with redis server");
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        }

        if(status && status !== REAL_TIME.RIDE_STATUS.IDLE){
            return res.status(200).json({
                message: 'Your previous ride request is processing, please wait.'
            });
        }

        // user are idle
        next();
    });
    
};

const storeRideRequest = (req, res) => {
    const userId = req.userIdentity._id;
    const currentLocation = req.body.location;
    const destination = req.body.destination;

    let completeRequest = Object.assign({}, req.body);
    completeRequest.riderId = userId;

    redisClient.rpush(
        REAL_TIME.REDIS_KEYS.RIDE_REQUEST, 
        JSON.stringify(completeRequest)
    );

    redisClient.hset(
        REAL_TIME.REDIS_KEYS.RIDE_STATUS, 
        userId, 
        REAL_TIME.RIDE_STATUS.IN_QUEUE
    );

    networkClient.POST(config.matching_engine_url+'trigger-real-time-match', {});

    return res.status(200).json({
        result: `real-time-ride-request received: riderId=${userId}, current location: (lat=${currentLocation.latitude}, long=${currentLocation.longitude}), destination: (lat=${destination.latitude}, long=${destination.longitude})`
    });
};

router.post('/real-time-ride-request',
    checkRiderStatus,
    storeRideRequest
);


module.exports = router;