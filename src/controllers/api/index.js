const express = require('express');
const router = express.Router();

const secretRouter = require('./secret');

router.use('/secret', secretRouter);

module.exports = router;