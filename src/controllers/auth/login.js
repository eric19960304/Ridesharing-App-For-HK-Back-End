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

const returnJWT = (req, res) => {

    if(!req.authenticated) {
        return res.status(401).json({
            message: 'Invalid email or password'
        });
    }

    if(!req.user.activated){
        return res.status(401).json({
            message: 'Email is not activated'
        });
    }

    const user = {
        email: req.user.email,
        nickname: req.user.nickname
    };

    res.status(200).json({
        jwt: generateJWTToken(req.user),
        user
    });

};

/* 
/auth/login
*/

router.post('/',
    fetchUserByEmail,
    authenticateUserLogin,
    returnJWT
);


module.exports = router;
