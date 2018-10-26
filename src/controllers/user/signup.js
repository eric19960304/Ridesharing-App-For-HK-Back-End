const express = require('express');

const { createUser } = require('../../middlewares/user');
const { encryptPassword } = require('../../middlewares/auth');


const router = express.Router();


const endRule = (req, res) => {
    res.status(200).json({
        success: 'registration success'
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
    createUser,
    endRule
);

module.exports = router;
