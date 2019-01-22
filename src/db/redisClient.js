var redis = require('redis');

var redisClient = redis.createClient();
redisClient.on('error', (err) => {
    console.log("Error " + err);
});

redisClient.flushall();

module.exports = redisClient;