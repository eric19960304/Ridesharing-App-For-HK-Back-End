const mongoose = require('mongoose');
const uuidv1 = require('uuid/v1');

const { TempLink } = require('../../models');

const ObjectId = mongoose.Types.ObjectId;

const createTempLink = (req, res, next) => {
    /*
    consequence: req.createdTempLink
    */

    if('userIsExist' in req && req.userIsExist === true){
        return res.status(200).json({
            message: 'This email has been used!'
        });
    }

    const expiryDate = new Date(new Date().getTime() + 60 * 60 * 24 * 1000);

    const tempLink = new TempLink({
        _id: new ObjectId(),
        token: uuidv1(),
        purpose: 'resetPassword',
        expiryDate,
        userId: req.user._id
    });

    tempLink.save()
        .then((result) => {
            console.log('created tempLink:', result);
            req.createdTempLink = result;   // attach createdTempLink to req
            next();
        })
        .catch(err => {
            console.log('create tempLink error: ', err);
            return res.status(200).json({
                message: 'Something wrong! Please try again latter.'
            });
        });
};

const deleteTempLink = (req, res, next) => {
    /*
    consequence: None
    */

    const _id = req.tempLink._id;
    TempLink.findOneAndRemove({ _id })
        .exec()
        .then(() => {

            console.log('removed tempLink: ', _id);
            next();

        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
}

module.exports = {
    createTempLink,
    deleteTempLink
};