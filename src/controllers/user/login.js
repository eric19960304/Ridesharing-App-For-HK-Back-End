const express = require('express');

const { fetchUserByEmail } = require('../../middleware/user');
const { authenticateUserLogin } = require('../../middleware/auth');
const { generateJWTToken } = require('../../helpers');

const router = express.Router();

/*

User request format example:
{
  "email": "ericlauchiho@gmail.com",
  "password": "ericpassword"
}

*/

router.post(
    '/',
    fetchUserByEmail,
    authenticateUserLogin,
    (req, res) => {

        if (!req.authenticated) {
            return res.status(401).json({
                failed: 'Unauthorized Access'
            });
        }

        res.status(200).json({
            jwt: generateJWTToken(req.user)
        });

    }
);


module.exports = router;
