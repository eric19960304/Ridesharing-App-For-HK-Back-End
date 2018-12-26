const express = require('express');
const router = express.Router();

const secretRouter = require('./secret');
const driverRouter = require('./driver');

router.use('/secret', secretRouter);
router.use('/driver', driverRouter);

module.exports = router;