const express = require('express');

const { createUnactivatedUser, checkUserIsExist } = require('../../middlewares/user');
const { 
    createTempLink, 
    deleteTempLink,
    fetchTempLinkAndUserIdentity 
} = require('../../middlewares/tempLink');
const { fetchUserById } = require('../../middlewares/user');
const { encryptPassword } = require('../../middlewares/auth');
const mailClient = require('../../helpers/mailClient');
const config = require('../../../config');

const router = express.Router();


const extractUserInfoFromReqBody = (req, res, next) => {
    const { email, nickname } = req.body;
    const { encryptedPassword } = req;

    req.newUser = {
        email,
        nickname,
        encryptedPassword
    };

    next();
};

const returnResponse = (req, res) => {
    res.status(200).json({
        success: true
    });
};

const setTempLinkPurpose = (req, res, next) => {
    req.tempLinkPurpose = 'activateAccount';
    next();
};

const activateUser = (req, res, next) => {

    req.user.activated = true;
    req.user.save(
        (err, user) => {
            if (err){
                console.log(err);
                return res.status(500).json({
                    message: 'Something wrong! Please try again latter.'
                });
            }

            next();
        }
    );
};

const sendActivationEmail = (req, res, next) => {
    const { token } = req.createdTempLink;
    const { nickname, email } = req.user;
    const url = config.domainName + '/auth/signup/activate/' + token;
    const subject = 'Threeriders: Account Activation';
    const content = `Dear ${nickname}, <br/> Please click the following link to activate your account: <br/><a href="${url}">${url}</a><br/><br/>Threeriders HKUCS FYP 2018`;

    mailClient.send( email, subject, content);
    
    next();
};

/* 
/auth/signup
/auth/signup/activate/:token
*/

router.post('/',
    encryptPassword,
    extractUserInfoFromReqBody,
    checkUserIsExist,
    createUnactivatedUser,
    setTempLinkPurpose,
    createTempLink,
    sendActivationEmail,
    returnResponse
);

router.get('/activate/:token',
    fetchTempLinkAndUserIdentity,
    fetchUserById,
    activateUser,
    deleteTempLink,
    (req, res) => {
        return res.send('Your email has been activated successfully! You can login to your account now.');
    }
);


module.exports = router;
