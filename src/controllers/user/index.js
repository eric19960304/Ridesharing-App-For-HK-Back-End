const express = require('express');
const router = express.Router();

const loginRouter = require('./login');
const signupRouter = require('./signup');

router.use('/login', loginRouter);
router.use('/signup', signupRouter);

module.exports = router;