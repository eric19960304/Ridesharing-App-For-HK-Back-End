var redis = require('redis');

var redisClient = redis.createClient();
redisClient.on('error', (err) => {
    console.log("Error " + err);
});

// redisClient.flushall();
// console.log('Flushed all cache on Redis');

module.exports = redisClient;