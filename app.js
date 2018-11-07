const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const fs = require('fs');
const http = require('http');
const https = require('https');
const privateKey  = fs.readFileSync('/ssl_cert/server.key', 'utf8');
const certificate = fs.readFileSync('/ssl_cert/server.crt', 'utf8');
const ca = fs.readFileSync('/ssl_cert/ca.crt', 'utf8');

const userRouter = require('./src/controllers');
const config = require('./config');

const app = express();
const credentials = {
    key: privateKey, 
    cert: certificate,
    ca
};

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

console.log('using config:', config);

const httpServer = http.createServer(app);
const httpsServer = https.createServer(credentials, app);

httpServer.listen(80, () => {
    console.log('Server is running on Port 80');
});
httpsServer.listen(443, () => {
    console.log('Server is running on Port 443');
});