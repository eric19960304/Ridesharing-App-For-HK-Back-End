const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const message = new Schema({
    senderId: {type: String, required: true},
    receiverId: {type: String, required: true},
    message: {type: String, required: true},
    createdAt: {type: Date, required: true},
});

module.exports = mongoose.model('Message', message);
