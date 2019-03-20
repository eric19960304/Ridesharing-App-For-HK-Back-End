const express = require('express');
const router = express.Router();
const redisClient = require('../../../db/redisClient');

const { REDIS_KEYS } = require('../../../helpers/constants');
const config = require('../../../../config');


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
    const userId = req.userIdentity._id.toString();

    redisClient.hset(
        REDIS_KEYS.DRIVER_LOCATION, 
        userId, 
        JSON.stringify(req.body)
    );
    
    return res.status(200).json({
        result: `user location updated: userId=${userId}, lat=${longitude}, long=${latitude}`
    });
};

const getAllDriversLocations = (req, res) => {
    
    redisClient.hgetall(
        REDIS_KEYS.DRIVER_LOCATION,
        (err, locations) => {
            let locationList = [];
            for(const key in locations){
                locationList.push(JSON.parse(locations[key]));
            }
            return res.status(200).json(locationList);
        }
    );

    
};

router.post('/location-update',
    storeLocationToCache
);

router.post('/get-all-drivers-location',
    getAllDriversLocations
);

module.exports = router;