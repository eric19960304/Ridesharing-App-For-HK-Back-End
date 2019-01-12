const express = require('express');
const router = express.Router();
const redisClient = require('../../../db/redisClient');
const { REAL_TIME_RIDE_STATUS } = require('../../../helpers/constants');


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
    redisClient.hget("realTimeRideStatus", userId, (err, status)=>{
        if(err){
            console.log("something wrong with redis server");
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        }

        if(status && status !== REAL_TIME_RIDE_STATUS.IDLE){
            return res.status(200).json({
                message: 'Your previous ride request is processing, please wait.'
            });
        }

        // user are idle
        next();
    });
    
};

const printLocation = (req, res) => {
    const userId = req.userIdentity._id;
    const currentLocation = req.body.location;
    const destination = req.body.destination;

    let completeRequest = Object.assign({}, req.body);
    completeRequest.riderId = userId;

    redisClient.rpush("realTimeRideRequest", JSON.stringify(completeRequest));
    redisClient.hset("realTimeRideStatus", userId, REAL_TIME_RIDE_STATUS.IN_QUEUE);

    return res.status(200).json({
        result: `real-time-ride-request received: riderId=${userId}, current location: (lat=${currentLocation.latitude}, long=${currentLocation.longitude}), destination: (lat=${destination.latitude}, long=${destination.longitude})`
    });
};

router.post('/real-time-ride-request',
    checkRiderStatus,
    printLocation
);


module.exports = router;