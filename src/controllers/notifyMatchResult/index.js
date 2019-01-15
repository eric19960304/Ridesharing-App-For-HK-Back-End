const express = require('express');
const router = express.Router();

const realTimeRideRouter = require('./realTimeRide');

router.use('/real-time-ride', realTimeRideRouter);

module.exports = router;