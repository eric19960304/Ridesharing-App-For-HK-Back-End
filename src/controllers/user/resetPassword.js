const express = require('express');

const { fetchUserById, fetchUserByEmail } = require('../../middlewares/user');
const { createTempLink, deleteTempLink } = require('../../middlewares/tempLink');
const { encryptPassword } = require('../../middlewares/auth');
const mailClient = require('../../helpers/mailClient');
const { User, TempLink} = require('../../models');
const config = require('../../../config');

const router = express.Router();

const printRequest = (req, res, next) => { console.log(req.body); next(); };



const fetchTempLinkAndUserIdentity = (req, res, next) => {
    /*
    consequence: req.userIdentity & tempLink
    Type userIdentity = { _id: string, email: null }
    */

    const token = req.params.token;

    TempLink.findOne({ token })
        .exec()
        .then((tempLink) => {

            if (tempLink && tempLink.purpose === 'resetPassword' && 
                new Date() < new Date(tempLink.expiryDate) ) {

                const userIdentity = {
                    _id: tempLink.userId,
                    email: null
                };

                req.tempLink = tempLink;
                req.userIdentity = userIdentity;
                next();

            } else {
                return res.send('link not exists or expired');
            }

        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
};


const sendResetPasswordLinkToUserByMail = (req, res) => {
    const { token } = req.createdTempLink;
    const { username, email } = req.user;
    const url = config.domainName + '/user/reset-password/' + token;
    mailClient.send(
        email, 
        'Threeriders: Reset Password Link', 
        `Dear ${username}, <br/> Please click the following link to reset your password: <br/><a href="${url}">${url}</a><br/><br/>Threeriders HKUCS FYP 2018`
    );
    return res.status(200).json({
        message: 'link sent'
    });
};

const serveResetPasswordForm = (req, res) => {
    res.render('newPasswordForm', {
        username: req.user.username
    });
};

const changeUserPasword = (req, res, next) => {
    const newPassword = req.encrypted_password;

    req.user.password = newPassword;
    req.user.save(
        (err, user) => {
            if (err){
                console.log(err);
                return res.status(500).json({
                    message: 'Something wrong! Please try again latter.'
                });
            }

            console.log('Password updated: ', user);
            next();
        }
    );
};


/* 
/user/reset-password/request [POST]
/user/reset-password/:token [GET]
/user/reset-password/:token [POST]
*/

router.post('/request',
    fetchUserByEmail,
    createTempLink,
    sendResetPasswordLinkToUserByMail
);

router.get('/:token',
    printRequest,
    fetchTempLinkAndUserIdentity,
    fetchUserById,
    serveResetPasswordForm
);

router.post('/:token',
    printRequest,
    fetchTempLinkAndUserIdentity,
    fetchUserById,
    encryptPassword,
    changeUserPasword,
    deleteTempLink,
    (req, res) => {
        return res.send('Your password has been changed successfully!');
    }
);


module.exports = router;
