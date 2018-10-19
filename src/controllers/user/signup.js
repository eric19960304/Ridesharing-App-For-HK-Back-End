const express = require('express');
const bcrypt = require('bcrypt');
const mongoose = require('mongoose');
const ObjectId = mongoose.Types.ObjectId;

const User = require('../../models');

const router = express.Router();
const saltRound = 10;

router.post('/', (req, res) => {
  const { email, password } = req.body;

  bcrypt.hash(password, saltRound, (err, hashed_password) => {
    if(err) {
      // hash error
      res.status(500).json({
          error: err
      });
    }

    const user = new User({
      _id: new ObjectId(),
      email: email,
      password: hashed_password,
    });

    user.save()
    .then((result) => {
      console.log('created user:', result);
      res.status(200).json({
          success: 'registration success'
      });
    })
    .catch( err => {
      // db error
      res.status(500).json({
          error: err
      });
    });
    
 });
});

module.exports = router;
