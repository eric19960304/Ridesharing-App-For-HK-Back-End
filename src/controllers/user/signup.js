const express = require('express');

const { createUser, checkUserIsExist } = require('../../middlewares/user');
const { encryptPassword } = require('../../middlewares/auth');
const { generateJWTToken } = require('../../helpers');

const router = express.Router();


const endRule = (req, res) => {
    res.status(200).json({
        jwt: generateJWTToken(req.createdUser)
    });
};


const prepareUserInfo = (req, res, next) => {
    const { email } = req.body;
    const { encrypted_password } = req;

    req.newUser = {
        email,
        encrypted_password
    };

    next();
};

router.post('/',
    encryptPassword,
    prepareUserInfo,
    checkUserIsExist,
    createUser,
    endRule
);

module.exports = router;
