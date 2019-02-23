const express = require('express');

const redisClient = require('../../../db/redisClient');
const { REDIS_KEYS } = require('../../../helpers/constants');

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


const storeRideRequest = (req, res) => {
    const userId = req.userIdentity._id.toString();
    const startLocation = req.body.startLocation;
    const endLocation = req.body.endLocation;

    let completeRequest = Object.assign({}, req.body);
    completeRequest.userId = userId;

    redisClient.rpush(
        REDIS_KEYS.RIDE_REQUEST, 
        JSON.stringify(completeRequest)
    );

    return res.status(200).json({
        result: `real-time-ride-request received: userId=${userId}, start location: (lat=${startLocation.latitude}, long=${startLocation.longitude}), end Location: (lat=${endLocation.latitude}, long=${endLocation.longitude})`
    });
};

router.post('/real-time-ride-request',
    storeRideRequest
);


module.exports = router;