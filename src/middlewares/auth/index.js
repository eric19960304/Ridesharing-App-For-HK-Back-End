const bcrypt = require('bcryptjs');
const { decodedJWT } = require('../../helpers/auth');

const costFactor = 10;

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
    hash the password submitted by user

    consequence: modify req.body.password
    */
    const { password } = req.body;

    bcrypt.hash(
        password, 
        costFactor, 
        (err, encryptedPassword) => {
            if (err) {
                // hash error
                return res.status(500).json({
                    error: err
                });
            }

            req.body.password = encryptedPassword;

            next();

        }
    );
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