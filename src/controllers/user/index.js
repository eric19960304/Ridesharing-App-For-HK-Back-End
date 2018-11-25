const express = require('express');
const router = express.Router();

const loginRouter = require('./login');
const signupRouter = require('./signup');
const resetPasswordRouter = require('./resetPassword');

router.use('/login', loginRouter);
router.use('/signup', signupRouter);
router.use('/reset-password', resetPasswordRouter);

module.exports = router;