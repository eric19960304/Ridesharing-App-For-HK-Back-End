const express = require('express');
const router = express.Router();

const config = require('../../../../config');

/* 
/api/secret/google-map-api-key
*/

const returnGoogleMapAPIKey = (req, res) => {
    res.status(200).json({
        googleMapApiKey: config.google_map_api_key
    });
};

router.post('/google-map-api-key',
    returnGoogleMapAPIKey,
);


module.exports = router;