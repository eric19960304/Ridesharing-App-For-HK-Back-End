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
            message: 'Email field missing'
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
                    message: 'Email not found'
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
                    message: 'Userid not found'
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


const createUnactivatedUser = (req, res, next) => {
    /*
    consequence: req.user
    */

    if('userIsExist' in req && req.userIsExist === true){
        return res.status(200).json({
            message: 'This email has been used!'
        });
    }

    const user = new User({
        _id: new ObjectId(),
        activated: false,
        ...req.newUser
    });

    user.save()
        .then((result) => {
            req.user = result;   // attach user to req
            next();
        })
        .catch(err => {
            console.log('create user error: ', err);
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        });
};


const updateUser = (req, res, next) => {
    /*
    consequence: modify req.user
    */

    for(const key in req.updatedUserInfo){
        if(req.updatedUserInfo[key]){
            req.user[key] = req.updatedUserInfo[key];
        }
    }
    
    req.user.save()
        .then(() => {
            next();
        })
        .catch(err => {
            console.log('update user error: ', err);
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        });
};

const findUsersPushTokens = (req, res, next) => {
    /*
    consequence: req.usersPushTokens
    [ 
        {
            userId: string,
            pushTokens: [string]
        }
    ]
    */

    User.find({ '_id': { $in: req.userIds} })
        .exec()
        .then((users) => {

            const usersPushTokens = [];
            users.forEach(user => {
                usersPushTokens.push({
                    userId: user._id,
                    pushTokens: user.pushTokens
                });
            });

            req.usersPushTokens = usersPushTokens;
            next();
        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
};


const findUsers = (req, res, next) => {

    // consequence: req.users

    User.find({ '_id': { $in: req.userIds} })
        .exec()
        .then((users) => {

            
            req.users = users;
            next();
        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
};

module.exports = {
    fetchUserByEmail,
    fetchUserById,
    checkUserIsExist,
    createUnactivatedUser,
    updateUser,
    findUsersPushTokens,
    findUsers
};