const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const config = require('../../../config')
const User = require('../../models');

const router = express.Router();

/*

User request format example:
{
  "email": "ericlauchiho@gmail.com",
  "password": "ericpassword"
}

*/

router.post('/', function(req, res){
  const { email, password } = req.body;

  User.findOne({ email })
  .exec()
  .then((user) => {

    bcrypt.compare(
      password, 
      user.password, 
      (err, result) => { // start of callback function
        if(err) {
          return res.status(401).json({
            error: err
          });
        }

        if(result) {
          const JWTToken = jwt.sign(
            {
              email: user.email,
              _id: user._id
            },
            config.jwt_secret,
            
          );

          return res.status(200).json({
            jwt: JWTToken
          });
        }

        // otherwise
        return res.status(401).json({
            failed: 'Unauthorized Access'
        });
      } // end of callback function
    );
  })
  .catch(error => {
     res.status(500).json({
        error: error
     });
  });;
});

module.exports = router;
