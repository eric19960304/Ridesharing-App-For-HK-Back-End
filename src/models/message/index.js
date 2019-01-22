const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const message = new Schema({
    _id: {type: String, required: true},
    senderId: {type: String, required: true},
    receiverId: {type: String, required: true},
    text: {type: String, required: true},
    createdAt: {type: Date, required: true}
});

module.exports = mongoose.model('Message', message);
