const express = require('express');
const router = express.Router();

const secretRouter = require('./secret');
const driverRouter = require('./driver');
const userRouter = require('./user');

router.use('/secret', secretRouter);
router.use('/driver', driverRouter);
router.use('/user', userRouter);

module.exports = router;