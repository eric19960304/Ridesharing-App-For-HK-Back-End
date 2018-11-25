const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

const tempLink = new Schema({
    _id: ObjectId,
    token: { type: String, unique: true, required: true },
    purpose: { type: String, required: true },
    expiryDate: { type: String, required: true },
    userId: { type: ObjectId, required: true, ref: 'User' }
});

module.exports = mongoose.model('TempLink', tempLink);