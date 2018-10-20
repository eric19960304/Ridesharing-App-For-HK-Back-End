
const bcrypt = require('bcrypt');

const saltRound = 10;

const authenticateUserLogin = (req, res, next) => {
    /*
    assume req.user exist
    glue authenticated bool variable to req object to indicate the result of user authentication
    */

    const { password } = req.body;
    const { user } = req;

    bcrypt.compare(
        password,
        user.password,
        (err, result) => { // start of callback function
            if (err) {
                console.log(err);
                req.authenticated = false;
            }

            req.authenticated = !!result;

            next();

        } // end of callback function
    );

}


const encryptPassword = (req, res, next) => {
    /*
    glue encrypted_password string variable to req object if password can be hashed
    */
    const { email, password } = req.body;

    bcrypt.hash(password, saltRound, (err, encrypted_password) => {
        if (err) {
            // hash error
            res.status(500).json({
                error: err
            });
        }

        req.encrypted_password = encrypted_password;

        next();

    });
}


module.exports = {
    authenticateUserLogin,
    encryptPassword
};