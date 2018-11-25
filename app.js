const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const http = require('http');
const https = require('https');

const { userRouter, testRouter} = require('./src/controllers');
const config = require('./config');

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(bodyParser.json());
app.set('view engine', 'pug');
app.set('views', './src/views');


// db
const MongoClient = require('./src/db');
const mongoClient = new MongoClient(config);
mongoClient.connect();

// static files
app.use(express.static('public'));

// routes
app.use('/user', userRouter);
app.use('/test', testRouter);


console.log('using config:', config);

const httpServer = http.createServer(app);

httpServer.listen(80, () => {
    console.log('Server is running on Port 80');
});

if(process.env.PROD){
    console.log('production mode');
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
}
