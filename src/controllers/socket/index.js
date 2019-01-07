const express = require('express');
const router = express.Router();
const { Message } = require('../../models');
// const httpServer = require('../../app.js')(httpServer);
// const socketio = require('socket.io');

module.exports = function (socketio) {

    //const websocket = socketio(server);
    users = {}

    // The event will be called when a client is connected.
    socketio.on('connection', (socket) => {
        console.log('A client just joined on', socket.id);
        socket.on('userJoin', (user) => onUserJoined(user,socket));
        socket.on('message', (message) => onMessageReceived(message, socket));
    });

    const onUserJoined = (message, socket) => {
        console.log(message);
        user = message.text
        if (!(user in users)) {
            sendExistingMessages(user, socket);
        } else {
          users[user] = socket.id;
          sendExistingMessages(user, socket);
        }
    }
    
    const sendExistingMessages = (user, socket) => {
        //let receiverId = user;
    
        Message.find({ $or: [ { 'senderId': user }, { 'recieverId': user } ]  })
            .sort({ 'createdAt': -1 })
            .exec(function (err, message) {
                if (err){
                    console.log(err);
                    return res.status(200).json({
                        message: 'Something wrong! Please try again latter.'
                    });
                }else{
                    if (!message.length) return;
                    // for(var i = 0; i < message.length; i++){
                    //     message[i].user = user;
                    //     console.log(message[i]);
                    // }
                    socket.emit('message', messages);
                }
            });

            // .then((message) => {
            //     console.log(message);
            //     console.log(message.toObject());
            //     var newMessage = message.toObject();
            //     // If there aren't any messages, then return.
            //     if (!message.length) return;
            //     for(var i = 0; i < newMessage.length; i++){
            //         newMessage[i].user = user;
    
            //     }
            //     console.log(newMessage)
            //     socket.emit('message', newMessage.reverse());
            // })
            // .catch(err => {
            //     console.log(err);
            //     return res.status(200).json({
            //         message: 'Something wrong! Please try again latter.'
            //     });
            // });
    
            //socket.clients[senderSocket].emit();
    }

    const onMessageReceived = (message, senderSocket) => {
    
        console.log(message);
    
        const newMessage = new Message({
            senderId: message.user.id,
            receiverId: 'server',
            message: message.text,
            createdAt: message.createdAt
        });
    
        newMessage.save()
            .catch(err => {
                console.log('insert message error: ', err);
                return res.status(200).json({
                    message: 'Something wrong! Please try again latter.'
                });
            });
    }

    return router;
};