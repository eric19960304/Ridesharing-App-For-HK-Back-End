const express = require('express');

const { createUser } = require('../../middlewares/user');
const { encryptPassword } = require('../../middlewares/auth');


const router = express.Router();


router.post(
    '/',
    encryptPassword,
    (req, res, next) => {
        const { email } = req.body;
        const { encrypted_password } = req;

        req.newUser = {
            email,
            encrypted_password
        };

        next();
    },
    createUser,
    (req, res) => {
        res.status(200).json({
            success: 'registration success'
        });
    }
);

module.exports = router;
