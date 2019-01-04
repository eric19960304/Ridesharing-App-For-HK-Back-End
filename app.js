const express = require('express');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const http = require('http');
const https = require('https');

const { authRouter, testRouter, apiRouter} = require('./src/controllers');
const { verifyJwt } = require('./src/middlewares/auth');
const config = require('./config');


const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(bodyParser.json());
app.set('view engine', 'pug');
app.set('views', './src/views');


// db
const MongoClient = require('./src/db/mongoClient');
const mongoClient = new MongoClient(config);
mongoClient.connect();

// static files
app.use(express.static('public'));

// print request for all routes
const printRequest = (req, res, next) => { console.log(req.body); next(); };
app.use(printRequest);

/*
All routes:
/auth/login [POST]
/auth/signup [POST]
/auth/reset-password/request [POST]
/auth/reset-password/:token [GET]
/auth/reset-password/:token [POST]
/api/secret/google-map-api-key [POST]
/api/driver/location-update [POST]
/api/user/edit-profile [POST]
*/
app.use('/auth', authRouter);
app.use(
    '/api', 
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    apiRouter
);
app.use(
    '/test', 
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    testRouter
);


console.log('using config:', config);

const httpServer = http.createServer(app);

if(process.env.PROD){
    console.log('production mode');

    httpServer.listen(80, () => {
        console.log('Server is running on Port 80');
    });

    const fs = require('fs');
    const privateKey  = fs.readFileSync('/ssl_cert/server.key', 'utf8');
    const certificate = fs.readFileSync('/ssl_cert/server.crt', 'utf8');
    const ca = fs.readFileSync('/ssl_cert/ca.crt', 'utf8');
    const credentials = {
        key: privateKey, 
        cert: certificate,
        ca
    };
    const httpsServer = https.createServer(credentials, app);
    httpsServer.listen(443, () => {
        console.log('Server is running on Port 443');
    });
}else{
    console.log('development mode');
    
    httpServer.listen(80, () => {
        console.log('Server is running on Port 80');
    });
}
