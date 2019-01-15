const express = require('express');
const router = express.Router();

const secretRouter = require('./secret');
const driverRouter = require('./driver');
const userRouter = require('./user');
const riderRouter = require('./rider');

router.use('/secret', secretRouter);
router.use('/driver', driverRouter);
router.use('/user', userRouter);
router.use('/rider', riderRouter);


module.exports = router;