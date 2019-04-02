const mongoose = require('mongoose');
const ObjectId = mongoose.Types.ObjectId;

const { Message } = require('../models');

let clientuserIdToSocketIdMapping = {}; // all appeared clients info, key: userId, value: socket id

const onUserJoined = (message, socket) => {
    clientuserIdToSocketIdMapping[message.userId] = socket.id;
    sendExistingMessages(message.userId, socket);
};

const onUserLeft = (message) => {
    delete clientuserIdToSocketIdMapping[message.userId];
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
                            _id: 2,
                            name: 'System'
                        },
                        text: message.text,
                        createdAt: message.createdAt
                    };
                    _messages.push(m);
                });
                socket.emit('message', _messages);
                Message.update(
                    { $or: [ { 'senderId': userId }, { 'receiverId': userId } ]  }, 
                    { 'isRead': true }, 
                    {multi: true},
                    (error)=>{
                        if(error){
                            console.log(error);
                        }
                    }
                );
            }
        });
};

const onUserClearUnread = (message) => {
    Message.update(
        { $or: [ { 'senderId': message.userId }, { 'receiverId': message.userId } ]  }, 
        { 'isRead': true }, 
        {multi: true},
        (error)=>{
            if(error){
                console.log(error);
            }
        }
    );
};

// const onMessageReceived = (message) => {
    
//     console.log('received message: ', message);

//     const newMessage = new Message({
//         _id: new ObjectId(),
//         messageId: message.messageId,
//         senderId: message.user._id,
//         receiverId: 'system',
//         text: message.text,
//         createdAt: message.createdAt,
//     });

//     newMessage.save()
//         .catch(err => {
//             console.log('insert message error: ', err);
//         });
// };

module.exports = {
    clientuserIdToSocketIdMapping,
    onUserJoined,
    onUserLeft,
    // onMessageReceived,
    onUserClearUnread,
};