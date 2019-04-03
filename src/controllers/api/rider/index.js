const express = require('express');
const mongoose = require('mongoose');

const redisClient = require('../../../db/redisClient');
const { REDIS_KEYS } = require('../../../helpers/constants');

const router = express.Router();
const ObjectId = mongoose.Types.ObjectId;

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
        timestamp: number,
        estimatedOptimal: { distance: number, duration: number }
}
*/


const storeRideRequest = (req, res) => {
    const userId = req.userIdentity._id.toString();

    let completeRequest = Object.assign({}, req.body);
    completeRequest.userId = userId;
    completeRequest.id = new ObjectId();

    redisClient.rpush(
        REDIS_KEYS.RIDE_REQUEST, 
        JSON.stringify(completeRequest)
    );

    return res.status(200).json({
        result: "ok"
    });
};

const getAllRealTimeRideRequest = (req, res) => {
    redisClient.lrange(REDIS_KEYS.RIDE_REQUEST, 0, -1, (error, requests)=>{
        console.log(requests);
        return res.status(200).json(requests);
    });
};

router.post('/real-time-ride-request',
    storeRideRequest
);

router.post('/get-all-real-time-ride-request',
    getAllRealTimeRideRequest
);


module.exports = router;