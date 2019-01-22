const express = require('express');

const notificationClient = require('../../helpers/notificationClient');
const { findUsersPushTokens, findUsers } = require('../../middlewares/user');
const redisClient = require('../../db/redisClient');
const { REAL_TIME } = require('../../helpers/constants');
const uuidv4 = require('uuid/v4');

const router = express.Router();


/*

User request format example:
*/

const checkIfRequestIsFromLocalhost = (req, res, next) => {
    if(req.headers.host!=='localhost' && req.headers.host!=='127.0.0.1'){
        console.log('Restricted access');
        return res.status(200).json({
            message: 'Restricted access'
        });
    }
    next();
};

const prepareForFindUsersPushTokens = (req, res, next) => {
    const riderId = req.body.rider.userId;
    const driverId = req.body.driver.userId;
    req.userIds = [riderId, driverId];
    next();
};

const sendNotificationToUsers = (req, res) => {
    /*
    req.body format:
    
    */

    let pushTokens = [];
    req.usersPushTokens.forEach(obj => {
        pushTokens.push(...obj.pushTokens);
    });

    // remove duplications
    pushTokens = pushTokens.filter((elem, pos) => {
        return pushTokens.indexOf(elem) === pos;
    });

    notificationClient.notify(pushTokens, 'Ride match found! Please checkout message page for detail.');

    const driverId = req.body.driver.userId;
    const riderId = req.body.rider.userId;
    redisClient.hset(
        REAL_TIME.REDIS_KEYS.RIDE_STATUS, 
        riderId, 
        REAL_TIME.RIDE_STATUS.IDLE
    );

    const users = req.users;
    let rider = null;
    let driver = null;
    users.forEach( user => {
        if(user._id === riderId){
            rider = Object.assign({}, rider);
        }
        if(user._id === driverId){
            driver = Object.assign({}, driver);
        }
    });

    let broadcaseMessage = {
        _id: uuidv4(),
        user: {
            _id: 3,
            name: 'System'
        },
        text: `Match found: rider name: ${rider.nickname}, driver name: ${driver.nickname}`,
        createdAt: new Date(),
    };

    const socketio = req.app.get('socketio');
    socketio.broadcast.emit('message', broadcaseMessage);

    res.status(200).json({
        message: 'Notification sent'
    });
};

/* 
/notify-match-result/real-time-ride
*/

router.post('/',
    checkIfRequestIsFromLocalhost,
    prepareForFindUsersPushTokens,
    findUsersPushTokens,
    findUsers,
    sendNotificationToUsers
);


module.exports = router;
