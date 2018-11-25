let mongodb_url = 'mongodb://localhost:27017/threeriders';
const db_username = 'root';
const db_password = process.env.MONGODB_PASSWORD;
if(process.env.PROD){
    mongodb_url = `mongodb://${db_username}:${db_password}@localhost:27017/threeriders?authSource=admin`;
}
const config = {
    MONGODB_URI: mongodb_url,
    jwt_secret: process.env.JWT_SECRET || 'threeriders',
    mailConfig: {
        user: 'hkucsfyp2018threeriders@gmail.com',
        pass: process.env.GMAIL_PASSWORD || 'password'
    },
    domainName: 'https://demo.coder.faith'
};

module.exports = config;