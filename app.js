const express = require('express');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const http = require('http');
const https = require('https');

const { authRouter, testRouter, apiRouter, notifyMatchResultRouter } = require('./src/controllers');
const { verifyJwt } = require('./src/middlewares/auth');
const config = require('./config');
const socketClient = require('./src/helpers/socketClient');
const cronjobs = require('./src/helpers/cronjob');

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
const printRequest = (req, res, next) => { 
    console.log(`[${(new Date()).toLocaleDateString()}] ${req.url}`); 
    next(); 
};


app.use(printRequest);
app.use('/auth', authRouter);
app.use(
    '/api', 
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    apiRouter
);
app.use(
    '/notify-match-result',
    notifyMatchResultRouter
);
app.use(
    '/test', 
    verifyJwt,  // doorguard, if jwt valid, user info will be injected into req.userIdentity
    testRouter
);

console.log('using config:', config);

const httpServer = http.createServer(app);

let server = null;

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

    httpServer.listen(80, () => {
        console.log('Server is running on Port 80');
    });

    server = httpsServer;

}else{
    console.log('development mode');
    
    httpServer.listen(80, () => {
        console.log('Server is running on Port 80');
    });

    server = httpServer;
}

let socketio = require('socket.io')(server);
app.set('socketio', socketio);

socketio.on('connection', (socket) => {
    socket.on('userJoined', (message) => socketClient.onUserJoined(message, socket));
    socket.on('userClearUnread', (message) => socketClient.onUserClearUnread(message));
});


cronjobs.startAllCronJobs();