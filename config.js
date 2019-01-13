let mongodb_url = 'mongodb://localhost:27017/threeriders';
let domainName = 'http://localhost';
const db_username = 'root';
const db_password = process.env.MONGODB_PASSWORD;
if(process.env.PROD){
    mongodb_url = `mongodb://${db_username}:${db_password}@localhost:27017/threeriders?authSource=admin`;
    domainName = 'https://demo.coder.faith';
}
const config = {
    mongodb_url,
    jwt_secret: process.env.JWT_SECRET || 'threeriders',
    mailConfig: {
        user: 'hkucsfyp2018threeriders@gmail.com',
        pass: process.env.GMAIL_PASSWORD || 'password'
    },
    domainName,
    google_map_api_key: process.env.GOOGLE_MAP_API_KEY || 'apikeyNotFound',
    matching_engine_url: process.env.MATCHING_ENGINE_URL || 'http://localhost:5000'
};

module.exports = config;