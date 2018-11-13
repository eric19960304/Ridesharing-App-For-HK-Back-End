const express = require('express');
const router = express.Router();

const { verifyJwt } = require('../../middlewares/auth');

const endRule = (req, res) => {
    const userIdentity = req.userIdentity;
    res.status(200).json({
        message: 'hello ' + userIdentity.email.split('@')[0] + '!'
    });
};


router.post('/sayhello',
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    endRule,
);

module.exports = router;