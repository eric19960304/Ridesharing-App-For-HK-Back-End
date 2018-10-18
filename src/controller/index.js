let express = require('express');
let router = express.Router();

/* GET home page. */
router.get('/', (req, res, next) => {
  res.json({"a": "b"});
});

module.exports = router;
