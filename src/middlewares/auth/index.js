
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require('../../../config');

const saltRound = 10;

const authenticateUserLogin = (req, res, next) => {
    /*
    glue authenticated bool variable to req object to indicate the result of user authentication

    prerequisite: req.body.password & req.user.password
    consequences: req.authenticated | None
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

    prerequisite: req.body.password
    consequences: req.encrypted_password | None
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


const generateJWTToken = (user) => {
    return jwt.sign(
        {
            email: user.email,
            _id: user._id
        },
        config.jwt_secret,
    );
};


module.exports = {
    authenticateUserLogin,
    encryptPassword,
    generateJWTToken,
};