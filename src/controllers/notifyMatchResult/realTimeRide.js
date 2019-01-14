const express = require('express');
const notificationClient = require('../../helpers/notificationClient');
const { findUsersPushTokens } = require('../../middlewares/user');

const router = express.Router();

/*

User request format example:
*/

const prepareForFindUsersPushTokens = (req, res, next) => {
    const { rider, driver } = req.body;
    req.userIds = [ rider.userId, driver.userId ];
    next();
};

const sendNotificationToUsers = (req, res) => {
    let pushTokens = [];
    req.usersPushTokens.forEach(obj => {
        pushTokens.push(...obj.pushTokens);
    });

    // remove duplications
    pushTokens = pushTokens.filter((elem, pos) => {
        return pushTokens.indexOf(elem) === pos;
    });

    notificationClient.notify([pushTokens], 'Ride match found! Please checkout message page for detail.');

    res.status(200).json({
        message: 'Notification sent'
    });
};

/* 
/notify-match-result/real-time-ride
*/

router.post('/',
    prepareForFindUsersPushTokens,
    findUsersPushTokens,
    sendNotificationToUsers
);


module.exports = router;
