const express = require('express');

const { fetchUserByEmail } = require('../../middlewares/user');
const { authenticateUserLogin } = require('../../middlewares/auth');
const { generateJWTToken } = require('../../helpers/auth');

const router = express.Router();

/*

User request format example:
{
  "email": "ericlauchiho@gmail.com",
  "password": "ericpassword"
}

*/

const printRequest = (req, res, next) => { console.log(req.body); next(); };

const returnJWT = (req, res) => {

    if (!req.authenticated) {
        return res.status(401).json({
            message: 'Invalid email or password'
        });
    }

    res.status(200).json({
        jwt: generateJWTToken(req.user)
    });

};

/* 
/user/login
*/

router.post('/',
    printRequest,
    fetchUserByEmail,
    authenticateUserLogin,
    returnJWT
);


module.exports = router;
