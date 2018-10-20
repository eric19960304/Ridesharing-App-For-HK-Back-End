const mongoose = require('mongoose');

const User = require('../../models');

const ObjectId = mongoose.Types.ObjectId;


const fetchUserByEmail = (req, res, next) => {
    /*
    glue user object to req object if found

    prerequisite: req.body.email
    consequences: req.user | None
    */

    const { email } = req.body;

    User.findOne({ email })
        .exec()
        .then((user) => {

            if(user){
                req.user = user;
                next();
            }else{
                return res.status(401).json({
                    failed: "email not found"
                });
            }

        })
        .catch(err => {

            return res.status(500).json({
                failed: err
            });

        });
}


const createUser = (req, res, next) => {
    /*
    create a user

    prerequisite: req.newUser.email & req.newUser.email.encrypted_password
    consequences: create a user record on database
    */

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

            return res.status(500).json({
                failed: err
            });
        });
}

module.exports = {
  fetchUserByEmail,
  createUser
};