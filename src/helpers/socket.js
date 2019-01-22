const mongoose = require('mongoose');
const ObjectId = mongoose.Types.ObjectId;

const { Message } = require('../models');

let users = {};  // this is a list of socket ids for all users

const onUserJoined = (message, socket) => {

    let userEmail = message.email;
    users[userEmail] = socket.id;
    sendExistingMessages(userEmail, socket);
};

const sendExistingMessages = (userEmail, socket) => {

    Message.find({ $or: [ { 'senderId': userEmail }, { 'recieverId': userEmail } ]  })
        .sort({ 'createdAt': -1 })
        .exec( (err, messages) => {
            if (err){
                console.log(err);
            }else{
                console.log('sendExistingMessages:messages', messages);
                if (!messages.length) return;
                let _messages = [];
                for(let i = 0; i < messages.length; i++){
                    let m = Object.assign({}, messages[i]._doc);
                    m.user = { _id: userEmail };
                    m._id = m.messageId;
                    delete m.messageId;
                    _messages.push(m);
                }
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

module.exports = {
    onUserJoined,
    onMessageReceived,
};