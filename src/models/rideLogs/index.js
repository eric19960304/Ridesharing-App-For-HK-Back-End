const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

const rideLogs = new Schema({
    _id: ObjectId,
    driverId: { type: ObjectId, required: true, ref: 'User' },
    riderId: { type: ObjectId, required: true, ref: 'User' },
    startLocation: {
        type: {
            latitude: { type: Number },
            longitude: { type: Number}
        },
        required: true
    },
    endLocation: {
        type: {
            latitude: { type: Number },
            longitude: { type: Number}
        },
        required: true
    },
    requestedDate: {type: Date, required: true},
    matchedDate: {type: Date},
    finishedDate: {type: Date}
});

module.exports = mongoose.model('RideLogs', rideLogs);
