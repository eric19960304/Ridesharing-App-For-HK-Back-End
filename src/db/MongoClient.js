const mongoose = require('mongoose');

class MongoClient {

    constructor(config) {
        this._config = config;
    }

    getMongoUrl() {
        return this._config.mongodb_url;
    }

    connect() {
        return mongoose.connect(
            this.getMongoUrl(),
            { useNewUrlParser: true }
        );
    }

}

module.exports = MongoClient;