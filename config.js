

const config = {
    MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/threeriders',
    jwt_secret: process.env.JWT_SECRET || 'threeriders',
};

if( !('JWT_SECRET' in process.env) ){
    console.log("Warning! JWT_SECRET not in env vairable, using default secret (" + config.jwt_secret + ") instead.");
}

module.exports = config;