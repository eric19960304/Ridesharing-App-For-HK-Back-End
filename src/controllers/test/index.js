const express = require('express');
const router = express.Router();

const { verifyJwt } = require('../../middlewares/auth');
const MailClient = require('../../helpers/mailClient');

/* 
/test/sayhello
/test/sendemail
*/

const sayhello = (req, res) => {
    const userIdentity = req.userIdentity;
    const mailClient = new MailClient();
    mailClient.sendTestMail();
    res.status(200).json({
        message: 'hello ' + userIdentity.email.split('@')[0] + '!'
    });
};

const sendEmail = (req, res) => {
    const mailClient = new MailClient();
    mailClient.sendTestMail();
    res.status(200).json({
        message: 'email sent'
    });
};

router.post('/sayhello',
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    sayhello,
);

router.post('/sendemail',
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    sendEmail,
);

module.exports = router;