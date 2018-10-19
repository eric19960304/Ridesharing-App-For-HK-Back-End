const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const bodyParser = require('body-parser');

const userRouter = require('./src/controllers');
const config = require('./config');

const app = express();

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.json());

// db
const MongoClient = require('./src/db');
const mongoClient = new MongoClient(config);
mongoClient.connect();

// routes
app.use('/user', userRouter);

/*

All routes:
/user/signup
/user/login

*/
const PORT = 3000;
app.listen(PORT, () => {
    console.log('Server is running on Port', PORT);
});