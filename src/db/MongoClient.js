const mongoose = require('mongoose');

class MongoClient {
  
    constructor (config) {
    this._config = config;
  }

  getMongoUrl() {
    return this._config.MONGODB_URI;
  }

  connect () {
    return mongoose.connect(
      this.getMongoUrl(),
      { useNewUrlParser: true }
      );
  }
  
}

module.exports = MongoClient;