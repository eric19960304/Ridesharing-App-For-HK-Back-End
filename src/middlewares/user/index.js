const mongoose = require('mongoose');

const User = require('../../models');

const ObjectId = mongoose.Types.ObjectId;


const fetchUserByEmail = (req, res, next) => {
    /*
    glue user object to req object if found
    */

    const { email } = req.body;

    User.findOne({ email })
        .exec()
        .then((user) => {

            if (user) {
                req.user = user;
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

const checkUserIsExist = (req, res, next) => {
    /*
    glue boolean variable to req object if user exists
    */

    const { email } = req.newUser;

    User.findOne({ email })
        .exec()
        .then((user) => {

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
    create a user
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
            req.createdUser = result;
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
    checkUserIsExist,
    createUser
};