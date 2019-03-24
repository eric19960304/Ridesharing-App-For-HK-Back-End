const cronJob = require("cron").CronJob;

const redisClient = require('../db/redisClient');
const { REDIS_KEYS } = require('./constants');
const { isDriverOnline } = require('./driver');

const removeOfflineDriverLocations = () => {
    const t = new Date();
    console.log(`[${t.toLocaleString()}] CronJob: removeOfflineDriverLocations`);
    redisClient.hgetall(
        REDIS_KEYS.DRIVER_LOCATION,
        (err, locations) => {
            for(const key in locations){
                const location = JSON.parse(locations[key]);
                if(!isDriverOnline(location)){
                    redisClient.hdel(REDIS_KEYS.DRIVER_LOCATION, key);
                }
            }
        }
    );
};

const startAllCronJobs = () => {
    // Run this cron job every 1 minute
    new cronJob(
        "* * * * *", 
        removeOfflineDriverLocations,
        null, 
        true
    );
};

module.exports = {
    startAllCronJobs
};