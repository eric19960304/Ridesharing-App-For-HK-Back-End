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

            req.user = user;
            next();

        })
        .catch(err => {

            res.status(500).json({
                failed: err
            });

        });
}


const createUser = (req, res, next) => {

    const { email, encrypted_password } = req.newUser;

    const user = new User({
        _id: new ObjectId(),
        email: email,
        password: encrypted_password,
    });

    user.save()
        .then((result) => {
            console.log('created user:', result);
            next();
        })
        .catch(err => {

            res.status(500).json({
                failed: err
            });
        });
}

module.exports = {
  fetchUserByEmail,
  createUser
};