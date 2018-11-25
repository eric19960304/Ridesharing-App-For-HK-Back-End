
const config = {
    MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/threeriders',
    jwt_secret: process.env.JWT_SECRET || 'threeriders',
    mailConfig: {
        user: 'hkucsfyp2018threeriders@gmail.com',
        pass: process.env.GMAIL_PASSWORD || 'password'
    }
};

module.exports = config;