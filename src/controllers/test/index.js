const express = require('express');
const router = express.Router();

const { verifyJwt } = require('../../middlewares/auth');
const mailClient = require('../../helpers/mailClient');

/* 
/test/sayhello
/test/sendemail
*/

const sayhello = (req, res) => {
    const userIdentity = req.userIdentity;
    res.status(200).json({
        message: 'hello ' + userIdentity.email.split('@')[0] + '!'
    });
};

const sendEmail = (req, res) => {
    mailClient.send('ericlauchiho@gmail.com', 'test subject', '<a href="https://i.cs.hku.hk/fyp/2018/fyp18028/">link</a>,  test content.');
    res.status(200).json({
        message: 'email sent'
    });
};

const gettest = (req, res) => {
    res.send('hello world');
};

router.get('/gettest',
    gettest
);

router.post('/sayhello',
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    sayhello,
);

router.post('/sendemail',
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    sendEmail,
);

module.exports = router;