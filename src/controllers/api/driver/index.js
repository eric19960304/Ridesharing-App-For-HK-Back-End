const express = require('express');
const router = express.Router();

/* 
/api/driver/location-update
*/

const printLocation = (req, res) => {
    const latitude = req.body.location.latitude;
    const longitude = req.body.location.longitude;
    const email = req.userIdentity.email; 
    res.status(200).json({
        result: `user location updated: email=${email}, lat=${longitude}, long=${latitude}`
    });
};

router.post('/location-update',
    printLocation
);


module.exports = router;