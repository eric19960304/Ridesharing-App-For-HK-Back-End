const express = require('express');
const router = express.Router();

const mailClient = require('../../helpers/mailClient');
const notificationClient = require('../../helpers/notificationClient');

const sayhello = (req, res) => {
    const userIdentity = req.userIdentity;
    res.status(200).json({
        message: 'Hello ' + userIdentity.email.split('@')[0] + '!'
    });
};

const sendEmail = (req, res) => {
    mailClient.send('ericlauchiho@gmail.com', 'test subject', '<a href="https://i.cs.hku.hk/fyp/2018/fyp18028/">link</a>,  test content.');
    res.status(200).json({
        message: 'Email sent'
    });
};

const gettest = (req, res) => {
    res.send('hello world');
};

const pushNotif = (req, res) => {
    const pushToken = req.body.pushToken;

    notificationClient.notify([pushToken], 'test notification ^_^', {message: 'test notification ^_^'});

    res.status(200).json({
        message: 'Notification sent'
    });
};

/* 
/test/sayhello
/test/sendemail
/test/push-notification
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

router.post('/push-notification',
    pushNotif
);

module.exports = router;