const express = require('express');
const mongoose = require('mongoose');

const notificationClient = require('../../helpers/notificationClient');
const { findUsersPushTokens, findUsers } = require('../../middlewares/user');
const redisClient = require('../../db/redisClient');
const { REDIS_KEYS } = require('../../helpers/constants');
const uuidv4 = require('uuid/v4');
const { Message } = require('../../models');
const socketClient = require('../../helpers/socketClient');


const ObjectId = mongoose.Types.ObjectId;
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

const sendNotificationAndMessageToUsers = (req, res) => {
    /*
    req.body format:
    {
        rider: {
            userId: string,
            startLocation: {
                latitude: number,
                longitude: number
            },
            endLocation: {
                latitude: number,
                longitude: number
            }
            timestamp: number
        },
        driver: {
            userId: string,
            location:  {
                "accuracy": number,
                "altitude": number,
                "altitudeAccuracy": number,
                "heading": number,
                "latitude": number,
                "longitude": number,
                "speed": number
            },
            timestamp: number
        }
    } */

    let pushTokens = [];
    req.usersPushTokens.forEach(obj => {
        pushTokens.push(...obj.pushTokens);
    });

    // remove duplications
    pushTokens = pushTokens.filter((elem, pos) => {
        return pushTokens.indexOf(elem) === pos;
    });

    // send notification
    notificationClient.notify(pushTokens, 'Ride match found! Please checkout message page for detail.');

    
    const riderId = req.body.rider.userId;
    const driverId = req.body.driver.userId;

    // decrement the seat number of driver
    redisClient.HINCRBY(REDIS_KEYS.SEAT_NUM, String(driverId), -1);

    const users = req.users;
    let riderName = null;
    let driverName = null;
    users.forEach( (user) => {
        if(user._id.toString() === riderId){  // debugged for 2 hours to find out user._id is not string, fuck this shit
            riderName = user.nickname;
        }else{
            driverName = user.nickname;
        }
    });
    
    const socketio = req.app.get('socketio');

    let message = null;
    users.forEach( (user) => {

        const userId = user._id.toString();

        let text = `Dear ${user.nickname}, you have a new ride match! `;

        if(userId === riderId) {
            text += `your driver is ${driverName}, contact: +85252252872`;
        }else{
            text += `your passenger is ${riderName}, contact: +85252252872`;
        }

        console.log(text);

        message = {
            _id: uuidv4(),
            user: {
                _id: 3,
                name: 'system'
            },
            text,
            createdAt: new Date(),
        };

        
        // send message via socket
        if(socketClient.clientuserIdToSocketIdMapping[userId]){
            socketio.to(socketClient.clientuserIdToSocketIdMapping[userId]).emit('message', message);
        }
        

        const newMessage = new Message({
            _id: new ObjectId(),
            messageId: message._id,
            senderId: 'system',
            receiverId: userId,
            text: message.text,
            createdAt: message.createdAt,
        });
    
        // store message to DB
        newMessage.save()
            .catch(err => {
                console.log('insert message error: ', err);
            });
    });

    return res.status(200).json({
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
    sendNotificationAndMessageToUsers
);


module.exports = router;
