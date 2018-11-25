
const bcrypt = require('bcrypt');
const { decodedJWT } = require('../../helpers/auth');

const saltRound = 10;

const authenticateUserLogin = (req, res, next) => {
    /*
    glue authenticated bool variable to req object to indicate the result of user authentication
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
            }

            req.authenticated = !!result;

            next();

        } // end of callback function
    );

};


const encryptPassword = (req, res, next) => {
    /*
    glue encrypted_password string variable to req object if password can be hashed
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
    glue encrypted_password string variable to req object if password can be hashed
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