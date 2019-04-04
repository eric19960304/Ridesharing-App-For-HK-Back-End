const mongoose = require('mongoose');
const Schema = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

const rideLogs = new Schema({
    _id: ObjectId,
    rideId: { type: String },
    driverId: { type: ObjectId, required: true, ref: 'User' },
    driverEmail: { type: String},
    riderId: { type: ObjectId, required: true, ref: 'User' },
    riderEmail: { type: String },
    algoVersion: { type: String, required: true },
    tag: { type: String },
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
    finishedDate: {type: Date},
    estimatedOptimal: {
        type: {
            distance: { type: Number},
            duration: { type: Number }
        }
    },
    estimatedWaitingCost: {
        type: {
            distance: { type: Number},
            duration: { type: Number }
        }
    },
});

module.exports = mongoose.model('RideLogs', rideLogs);
