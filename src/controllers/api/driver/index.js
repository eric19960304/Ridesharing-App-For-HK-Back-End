const express = require('express');
const router = express.Router();
const redisClient = require('../../../db/redisClient');

const { REAL_TIME } = require('../../../helpers/constants');


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

const storeLocationToCache = (req, res) => {
    const latitude = req.body.location.latitude;
    const longitude = req.body.location.longitude;
    const userId = req.userIdentity._id;

    redisClient.hset(
        REAL_TIME.REDIS_KEYS.DRIVER_LOCATION, 
        userId, 
        JSON.stringify(req.body)
    );
    
    return res.status(200).json({
        result: `user location updated: userId=${userId}, lat=${longitude}, long=${latitude}`
    });
};

router.post('/location-update',
    storeLocationToCache
);


module.exports = router;