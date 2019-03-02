const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

const user = new Schema({
    _id: ObjectId,
    email: { type: String, unique: true, required: true },
    password: { type: String, required: true },
    nickname: { type: String, required: true },
    activated: { type: Boolean, required: true },
    avatarSource: { type: String },
    pushTokens: [{ type: String }],
    carplate:{ type: String},
    contact:{ type: String},
    isDriver:{ type: Boolean},
});

module.exports = mongoose.model('User', user);