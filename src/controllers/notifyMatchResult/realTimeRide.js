const express = require('express');
const mongoose = require('mongoose');

const notificationClient = require('../../helpers/notificationClient');
const { findUsersPushTokens, findUsers } = require('../../middlewares/user');
const redisClient = require('../../db/redisClient');
const { REDIS_KEYS } = require('../../helpers/constants');
const uuidv4 = require('uuid/v4');
const { Message, RideLogs } = require('../../models');
const socketClient = require('../../helpers/socketClient');


const ObjectId = mongoose.Types.ObjectId;
const router = express.Router();


/*

req.body format for /notify-match-result/real-time-ride:
{   rider: {
        id: string,
        userId: string,
        startLocation: {
            latitude: number,
            longitude: number
        },
        endLocation: {
            latitude: number,
            longitude: number
        }
        timestamp: number,
        estimatedOptimal: {
            distance: number, duration: number
        }
    },
    driver: {
        userId: string,
        location:  {
            "latitude": number,
            "longitude": number
        }
    },
    algoVersion: string             }
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

const storeRideDetailsToRedis = (req, res, next) => {
    const driverId = req.body.driver.userId;

    req.users.forEach( (user) => {
        if(user._id.toString() === driverId){ 
            req.driver = user;
        }else{
            req.rider = user;
        }
    });

    if(req.users[0]._id.toString()===req.users[1]._id.toString()){
        req.rider = req.users[0];
    }

    let driverOngoingRideList;
    redisClient.HGET(REDIS_KEYS.DRIVER_ON_GOING_RIDE, driverId, (err, data)=>{
        if(data===null){
            // key not exist.
            driverOngoingRideList = [];
        }else{
            driverOngoingRideList =  JSON.parse(data);
        }

        let rideReq = Object.assign({}, req.body.rider);
        rideReq.requestedDate = (new Date(rideReq.timestamp)).toISOString(); // added for readibility
        rideReq.matchedDate = (new Date()).toISOString();  // added for readibility
        rideReq.isOnCar = false;
        
        driverOngoingRideList.push(rideReq);

        redisClient.HSET(REDIS_KEYS.DRIVER_ON_GOING_RIDE, driverId, JSON.stringify(driverOngoingRideList));

        next();
    });
};

const saveRideLogsToDB = (req, res, next) => {
    
    const riderReq = req.body.rider;
    const driverReq = req.body.driver;

    const newRideLogs = new RideLogs({
        _id: ObjectId(),
        rideId: riderReq.id,
        driverId: driverReq.userId,
        driverEmail: req.driver.email,
        riderId: riderReq.userId,
        riderEmail: req.rider.email,
        startLocation: {
            latitude: riderReq.startLocation.latitude,
            longitude: riderReq.startLocation.longitude
        },
        endLocation: {
            latitude: riderReq.endLocation.latitude,
            longitude: riderReq.endLocation.longitude
        },
        estimatedOptimal: riderReq.estimatedOptimal,
        requestedDate: new Date(riderReq.timestamp),
        matchedDate: new Date(),
        algoVersion: req.body.algoVersion,
        tag: 'caseStudy1'
    });

    // store ride logs to DB
    newRideLogs.save()
        .catch(err => {
            console.log('insert ride logs error: ', err);
        });
    
    next();
};

const sendNotificationAndMessageToUsers = (req, res) => {

    const driverId = req.body.driver.userId;
    const rider = req.rider;
    const driver = req.driver;
    const socketio = req.app.get('socketio');

    req.users.forEach( (user) => {

        const userId = user._id.toString();

        let text = `Dear ${user.nickname}, you have a new ride match! `;

        let displayDistance, displayDuration;
        if(req.body.rider.estimatedOptimal){
            displayDistance = req.body.rider.estimatedOptimal.distance;
            displayDuration = Math.round(req.body.rider.estimatedOptimal.duration/60);
        }else{
            displayDistance = 0;
            displayDuration = 0;
        }
        
        if(userId === driverId) {
            text += `your passenger is [${rider.nickname}], contact: +852${rider.contact}. Travel distance is ${displayDistance} m and estimated duration is ${displayDuration} mins`;
        }else{
            text += `your driver is [${driver.nickname}], contact: +852${driver.contact}, carplate: ${driver.carplate}. Travel distance is ${displayDistance} m and estimated duration is ${displayDuration} mins`;
        }
        
        let tokensForThisUser = req.usersPushTokens.filter( t => t.userId.toString()===userId)[0];
        tokensForThisUser = tokensForThisUser.pushTokens;
        
        // remove duplications tokens
        tokensForThisUser = tokensForThisUser.filter((elem, pos) => {
            return tokensForThisUser.indexOf(elem) === pos;
        });

        if(tokensForThisUser.length>0){
            notificationClient.notify(tokensForThisUser, 'New Message:\n' + text);
        }

        console.log(text);

        const message = {
            _id: uuidv4(),
            user: {
                _id: 2,
                name: 'System'
            },
            text,
            createdAt: new Date(),
        };

        // send message via socket
        if(socketClient.clientuserIdToSocketIdMapping[userId]){
            socketio.to(socketClient.clientuserIdToSocketIdMapping[userId]).emit('message', [message]);
        }
        
        const newMessage = new Message({
            _id: new ObjectId(),
            messageId: message._id,
            senderId: 'system',
            receiverId: userId,
            text: message.text,
            createdAt: message.createdAt,
            isRead: false
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
    storeRideDetailsToRedis,
    saveRideLogsToDB,
    sendNotificationAndMessageToUsers
);


module.exports = router;
