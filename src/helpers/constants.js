const REAL_TIME = {
    RIDE_STATUS: {
        IDLE: 'idle',
        IN_QUEUE: 'inQueue',
        PROCESSING: 'processing',
        ON_RIDE: 'onRide'
    },
    REDIS_KEYS: {
        RIDE_REQUEST: 'realTimeRideRequest',
        RIDE_STATUS: 'realTimeRideStatus',
        DRIVER_LOCATION: 'driverLocation'
    }
};


module.exports = {
    REAL_TIME
};