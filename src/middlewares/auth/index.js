
const bcrypt = require('bcrypt');
const { decodedJWT } = require('../../helpers/auth');

const saltRound = 10;

const authenticateUserLogin = (req, res, next) => {
    /*
    consequence: req.authenticated
    */

    const { password } = req.body;
    const database_password = req.user.password;

    bcrypt.compare(
        password,
        database_password,
        (err, result) => { // start of callback function
            if (err) {
                console.log(err);
                req.authenticated = false;
            }else{
                req.authenticated = !!result;
            }

            next();

        } // end of callback function
    );

};


const encryptPassword = (req, res, next) => {
    /*
    attach encrypted_password to req if password can be hashed

    consequence: req.encrypted_password
    */
    const { password } = req.body;

    bcrypt.hash(password, saltRound, (err, encrypted_password) => {
        if (err) {
            // hash error
            return res.status(500).json({
                error: err
            });
        }

        req.encrypted_password = encrypted_password;

        next();

    });
};

const verifyJwt = (req, res, next) => {
    /*
    Verify JWT in the POST header and extract user identity

    consequence: req.userIdentity
    Type: userIdentity: { _id: string, email: string }
    */
    const JWT = req.get('JWT'); // get JWT from POST header

    if (!JWT) {
        return res.status(401).json({
            message: 'JWT Token not provided.'
        });
    }
    let userIdentity = null;
    try {
        userIdentity = decodedJWT(JWT);
    } catch (err) {
        return res.status(401).json({
            message: 'Unauthorized access'
        });
    }

    if(userIdentity){
        req.userIdentity = userIdentity;
    }

    next();

};

module.exports = {
    authenticateUserLogin,
    encryptPassword,
    verifyJwt,
};