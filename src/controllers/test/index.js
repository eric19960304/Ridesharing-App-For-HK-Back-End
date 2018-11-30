const express = require('express');
const router = express.Router();

const mailClient = require('../../helpers/mailClient');

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

/* 
/test/sayhello
/test/sendemail
*/

router.get('/gettest',
    gettest
);

router.post('/sayhello',
    sayhello,
);

router.post('/sendemail',
    sendEmail,
);

module.exports = router;