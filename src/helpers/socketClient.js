const mongoose = require('mongoose');
const ObjectId = mongoose.Types.ObjectId;

const { Message } = require('../models');

let clientuserIdToSocketIdMapping = {}; // all appeared clients info, key: userId, value: socket id

const onUserJoined = (message, socket) => {
    console.log('A client just joined on', socket.id);
    clientuserIdToSocketIdMapping[message.userId] = socket.id;
    sendExistingMessages(message.userId, socket);
};

const sendExistingMessages = (userId, socket) => {

    Message.find({ $or: [ { 'senderId': userId }, { 'receiverId': userId } ]  })
        .sort({ 'createdAt': -1 })
        .exec( (err, messages) => {
            if (err){
                console.log(err);
            }else{
                if (!messages.length) return;
                let _messages = [];
                messages.forEach( message => {
                    let m = {
                        _id: message.messageId,
                        user: { 
                            _id: message.senderId
                        },
                        senderId: message.senderId,
                        receiverId: message.receiverId,
                        text: message.text,
                        createdAt: message.createdAt
                    };
                    _messages.push(m);
                });

                socket.emit('message', _messages);
            }
        });
};

const onMessageReceived = (message) => {
    
    console.log('received message: ', message);

    const newMessage = new Message({
        _id: new ObjectId(),
        messageId: message.messageId,
        senderId: message.user._id,
        receiverId: 'system',
        text: message.text,
        createdAt: message.createdAt,
    });

    newMessage.save()
        .catch(err => {
            console.log('insert message error: ', err);
        });
};

module.exports = {
    clientuserIdToSocketIdMapping,
    onUserJoined,
    onMessageReceived,
};