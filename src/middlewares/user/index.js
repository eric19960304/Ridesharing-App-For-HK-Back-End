const mongoose = require('mongoose');

const { User } = require('../../models');

const ObjectId = mongoose.Types.ObjectId;


const fetchUserByEmail = (req, res, next) => {
    /*
    consequence: req.user
    */

    let email = null;
    if(req.body && req.body.email){
        email = req.body.email;
    }
    if(req.userIdentity && req.userIdentity.email){
        email = req.userIdentity.email;
    }

    if(email === null){
        return res.status(400).json({
            message: 'email field missing'
        });
    }

    User.findOne({ email })
        .exec()
        .then((user) => {

            if (user) {
                req.user = user;  // attach user's info to req
                next();
            } else {
                return res.status(401).json({
                    message: 'email not found'
                });
            }

        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
};

const fetchUserById = (req, res, next) => {
    /*
    consequence: req.user
    */

    const _id = req.userIdentity._id;

    User.findOne({ _id })
        .exec()
        .then((user) => {

            if (user) {
                req.user = user;  // attach user's info to req
                next();
            } else {
                return res.status(401).json({
                    message: 'userid not found'
                });
            }

        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
};

const checkUserIsExist = (req, res, next) => {
    /*
    consequence: req.userIsExist
    */

    const { email } = req.newUser;

    User.findOne({ email })
        .exec()
        .then((user) => {

            // attach userIsExist to req
            if(user === null){
                req.userIsExist = false;
            }else{
                req.userIsExist = true;
            }
            
            next();
        })
        .catch(err => {
            console.log(err);
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        });
};


const createUser = (req, res, next) => {
    /*
    consequence: req.createdUser
    */

    if('userIsExist' in req && req.userIsExist === true){
        return res.status(200).json({
            message: 'This email has been used!'
        });
    }

    const { email, encrypted_password, username } = req.newUser;

    const user = new User({
        _id: new ObjectId(),
        email: email,
        password: encrypted_password,
        username,
    });

    user.save()
        .then((result) => {
            console.log('created user:', result);
            req.createdUser = result;   // attach createdUser to req
            next();
        })
        .catch(err => {
            console.log('create user error: ', err);
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        });
};

module.exports = {
    fetchUserByEmail,
    fetchUserById,
    checkUserIsExist,
    createUser
};