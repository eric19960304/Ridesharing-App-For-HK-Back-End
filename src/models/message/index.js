const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

const message = new Schema({
    _id: ObjectId,
    messageId: {type: String, required: true},
    senderId: {type: String, required: true},
    receiverId: {type: String, required: true},
    text: {type: String, required: true},
    createdAt: {type: Date, required: true}
});

module.exports = mongoose.model('Message', message);
