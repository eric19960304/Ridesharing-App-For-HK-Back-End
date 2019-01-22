
const { Message } = require('../models');

let users = {};

const onUserJoined = (message, socket) => {
    //console.log(message);

    let user = message.text;
    users[user] = socket.id;
    sendExistingMessages(user, socket);
};

const sendExistingMessages = (user, socket) => {

    Message.find({ $or: [ { 'senderId': user }, { 'recieverId': user } ]  })
        .sort({ 'createdAt': -1 })
        .exec(function (err, messages) {
            if (err){
                console.log(err);
            }else{
                if (!messages.length) return;
                let _messages = [];
                for(var i = 0; i < messages.length; i++){
                    let m = Object.assign({}, messages[i]._doc);
                    m.user = { id: user};
                    _messages.push(m);
                }
                //console.log(_messages);
                socket.emit('message', _messages);
            }
        });
};

const onMessageReceived = (message) => {
    
    //console.log(message);

    const newMessage = new Message({
        senderId: message.user.id,
        receiverId: 'server',
        text: message.text,
        createdAt: message.createdAt,
        _id: message._id
    });

    newMessage.save()
        .catch(err => {
            console.log('insert message error: ', err);
        });
};

module.exports = {
    onUserJoined,
    onMessageReceived
};