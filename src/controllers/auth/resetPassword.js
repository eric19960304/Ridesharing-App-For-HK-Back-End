const express = require('express');

const { fetchUserById, fetchUserByEmail } = require('../../middlewares/user');
const { 
    createTempLink, 
    deleteTempLink, 
    fetchTempLinkAndUserIdentity 
} = require('../../middlewares/tempLink');
const { encryptPassword } = require('../../middlewares/auth');
const mailClient = require('../../helpers/mailClient');
const config = require('../../../config');

const router = express.Router();



const sendResetPasswordLinkToUserByMail = (req, res) => {
    const { token } = req.createdTempLink;
    const { nickname, email } = req.user;
    const url = config.domainName + '/user/reset-password/' + token;
    const subject = 'Threeriders: Reset Password Link';
    const content = `Dear ${nickname}, <br/> Please click the following link to reset your password: <br/><a href="${url}">${url}</a><br/><br/>Threeriders HKUCS FYP 2018`;
    mailClient.send( email, subject, content);
    return res.status(200).json({
        message: 'Link sent'
    });
};

const serveResetPasswordForm = (req, res) => {
    res.render('newPasswordForm', {
        nickname: req.user.nickname
    });
};

const changeUserPasword = (req, res, next) => {
    const newPassword = req.encryptedPassword;

    req.user.password = newPassword;
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

const ensureEmailNotExistAndSetTempLinkPurpose = (req, res, next) => {
    if('userIsExist' in req && req.userIsExist === true){
        return res.status(200).json({
            message: 'This email has been used!'
        });
    }

    req.tempLinkPurpose = 'resetPassword';
    next();
};


/* 
/auth/reset-password/request [POST]
/auth/reset-password/:token [GET]
/auth/reset-password/:token [POST]
*/

router.get('/:token',
    fetchTempLinkAndUserIdentity,
    fetchUserById,
    serveResetPasswordForm
);

router.post('/request',
    fetchUserByEmail,
    ensureEmailNotExistAndSetTempLinkPurpose,
    createTempLink,
    sendResetPasswordLinkToUserByMail
);

router.post('/:token',
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
