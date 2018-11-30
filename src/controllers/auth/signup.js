const express = require('express');

const { createUser, checkUserIsExist } = require('../../middlewares/user');
const { encryptPassword } = require('../../middlewares/auth');
const { generateJWTToken } = require('../../helpers/auth');

const router = express.Router();

const extractUserInfoFromReqBody = (req, res, next) => {
    const { email, username } = req.body;
    const { encrypted_password } = req;

    req.newUser = {
        email,
        username,
        encrypted_password
    };

    next();
};

const returnJWT = (req, res) => {
    res.status(200).json({
        jwt: generateJWTToken(req.createdUser)
    });
};


/* 
/auth/signup
*/

router.post('/',
    encryptPassword,
    extractUserInfoFromReqBody,
    checkUserIsExist,
    createUser,
    returnJWT
);

module.exports = router;
