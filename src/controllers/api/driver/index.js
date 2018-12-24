const express = require('express');
const router = express.Router();
const redis = require("redis");
const redisClient = require('../../../db/redisClient');


/* 
/api/driver/location-update
*/

const printLocation = (req, res) => {
    const latitude = req.body.location.latitude;
    const longitude = req.body.location.longitude;
    const userId = req.userIdentity._id;
    redisClient.hset("driverLocation", userId, JSON.stringify(req.body), redis.print);
    res.status(200).json({
        result: `user location updated: userId=${userId}, lat=${longitude}, long=${latitude}`
    });
};

router.post('/location-update',
    printLocation
);


module.exports = router;