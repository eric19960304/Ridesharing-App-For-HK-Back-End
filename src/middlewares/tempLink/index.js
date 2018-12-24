const mongoose = require('mongoose');
const uuidv1 = require('uuid/v1');

const { TempLink } = require('../../models');

const ObjectId = mongoose.Types.ObjectId;

const createTempLink = (req, res, next) => {
    /*
    consequence: req.createdTempLink
    */

    // expire in 24 hours
    const expiryDate = new Date(new Date().getTime() + 60 * 60 * 24 * 1000);

    const tempLink = new TempLink({
        _id: new ObjectId(),
        token: uuidv1(),
        purpose: req.tempLinkPurpose,
        expiryDate,
        userId: req.user._id
    });

    tempLink.save()
        .then((result) => {
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

            next();

        })
        .catch(err => {
            console.log(err);
            return res.status(500).json({
                message: 'Something wrong! Please try again latter.'
            });

        });
};

const fetchTempLinkAndUserIdentity = (req, res, next) => {
    /*
    consequence: req.userIdentity & req.tempLink
    Type userIdentity = { _id: string, email: null }
    */

    const token = req.params.token;

    TempLink.findOne({ token })
        .exec()
        .then((tempLink) => {

            if (tempLink && 
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

module.exports = {
    createTempLink,
    deleteTempLink,
    fetchTempLinkAndUserIdentity
};