const express = require('express');

const redisClient = require('../../../db/redisClient');
const { REAL_TIME } = require('../../../helpers/constants');

const router = express.Router();

/* 
/api/rider/real-time-ride-request
expected req.body format: {
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
    const startLocation = req.body.startLocation;
    const endLocation = req.body.endLocation;

    let completeRequest = Object.assign({}, req.body);
    completeRequest.userId = userId;

    redisClient.rpush(
        REAL_TIME.REDIS_KEYS.RIDE_REQUEST, 
        JSON.stringify(completeRequest)
    );

    redisClient.hset(
        REAL_TIME.REDIS_KEYS.RIDE_STATUS, 
        userId, 
        REAL_TIME.RIDE_STATUS.IN_QUEUE
    );

    return res.status(200).json({
        result: `real-time-ride-request received: userId=${userId}, start location: (lat=${startLocation.latitude}, long=${startLocation.longitude}), end Location: (lat=${endLocation.latitude}, long=${endLocation.longitude})`
    });
};

router.post('/real-time-ride-request',
    checkRiderStatus,
    storeRideRequest
);


module.exports = router;