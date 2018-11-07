const express = require('express');

const { fetchUserByEmail } = require('../../middlewares/user');
const { authenticateUserLogin } = require('../../middlewares/auth');
const { generateJWTToken } = require('../../helpers');

const router = express.Router();

/*

User request format example:
{
  "email": "ericlauchiho@gmail.com",
  "password": "ericpassword"
}

*/

const printRequest = (req, res, next) => { console.log(req.body); next(); };

const endRule = (req, res) => {

    if (!req.authenticated) {
        return res.status(401).json({
            message: 'Invalid email or password'
        });
    }

    res.status(200).json({
        jwt: generateJWTToken(req.user)
    });

};

router.post('/',
    printRequest,
    fetchUserByEmail,
    authenticateUserLogin,
    endRule
);


module.exports = router;
