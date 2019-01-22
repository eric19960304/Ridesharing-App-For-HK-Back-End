const mongoose = require('mongoose');
const ObjectId = mongoose.Types.ObjectId;

const { Message } = require('../models');

let users = {};  // this is a list of socket ids for all users

const onUserJoined = (message, socket) => {
    console.log(message);

    let user = message.text;
    users[user] = socket.id;
    sendExistingMessages(user, socket);
};

const sendExistingMessages = (user, socket) => {

    Message.find({ $or: [ { 'senderId': user }, { 'recieverId': user } ]  })
        .sort({ 'createdAt': -1 })
        .exec( (err, messages) => {
            if (err){
                console.log(err);
            }else{
                if (!messages.length) return;
                let _messages = [];
                for(let i = 0; i < messages.length; i++){
                    let m = Object.assign({}, messages[i]._doc);
                    m.user = { id: user };
                    m._id = m.messageId;
                    _messages.push(m);
                }
                //console.log(_messages);
                socket.emit('message', _messages);
            }
        });
};

const onMessageReceived = (message) => {
    
    console.log('recieved message: ', message);

    const newMessage = new Message({
        _id: new ObjectId(),
        messageId: message.messageId,
        senderId: message.user.id,
        receiverId: 'server',
        text: message.text,
        createdAt: message.createdAt,
    });

    newMessage.save()
        .catch(err => {
            console.log('insert message error: ', err);
        });
};

const startSocketServer = (server) => {
    const websocket = require('socket.io')(server);
    websocket.on('connection', (socket) => {
        console.log('A client just joined on', socket.id);
        socket.on('userJoined', (message) => onUserJoined(message, socket));
        socket.on('message', (message) => onMessageReceived(message));
    });
};

module.exports = {
    onUserJoined,
    onMessageReceived,
    startSocketServer
};