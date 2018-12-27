const express = require('express');
const router = express.Router();

const { authenticateUserLogin, encryptPassword } = require('../../../middlewares/auth');
const { fetchUserById, updateUser } = require('../../../middlewares/user');

/* 
/api/user/edit-profile
*/

const prepareForPasswordEncrypt = (req, res, next) => {
    if('newPassword' in req.body){
        req.body.password = req.body.newPassword;
        delete req.body.newPassword;
    }
    
    next();
};

const prepareUpdatedUserInfo = (req, res, next) => {
    req.updatedUserInfo = Object.assign({}, req.body);

    next();
};

const prepareUpdatedUserInfoAndPassword = (req, res, next) => {
    if(req.authenticated === true){
        req.body.password = req.encryptedPassword;
        delete req.encryptPassword;
        req.updatedUserInfo = Object.assign({}, req.body);
        next();
    }else{
        return res.status(401).json({
            message: 'Current password not correct!'
        });
    }
};

const returnResponse = (req, res) => {
    res.status(200).json({
        success: true
    });
};

router.post('/edit-profile',
    fetchUserById,
    prepareUpdatedUserInfo,
    updateUser,
    returnResponse
);

router.post('/edit-profile-with-password',
    fetchUserById,
    authenticateUserLogin,
    prepareForPasswordEncrypt,
    encryptPassword,
    prepareUpdatedUserInfoAndPassword,
    updateUser,
    returnResponse
);


module.exports = router;